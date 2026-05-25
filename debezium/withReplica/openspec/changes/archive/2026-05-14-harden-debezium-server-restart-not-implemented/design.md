## Context

`evaluate-debezium-server-ha` agregó probes mínimas a ambos manifests y midió empíricamente el RTO post-kill. Resultado relevante:

| Stack | time-to-Ready (mediana) | time-to-first-event (mediana) | gap |
|---|---|---|---|
| `cdc-mysql8` | 22.24s | 5.52s | 16.72s |
| `cdc-mysql57` | 22.16s | 6.11s | 16.05s |

El gap ~16s está dominado por `readinessProbe.initialDelaySeconds: 20`. Es decir, Debezium ya está sirviendo eventos al sink ~5–6s después del delete, pero la primera evaluación de la sonda recién ocurre a +20s, por lo que `kubectl get pods` reporta `Ready=False` durante un período en el que el sistema **ya está funcional**. Esto es problemático porque:

1. Cualquier herramienta que use `kubectl wait --for=condition=Ready` o métricas de Ready (Prometheus, alertas) reporta indisponibilidad falsa por 15+ segundos extra.
2. Hace que cualquier rollout secuencial (en un futuro multi-stack) sea más lento de lo necesario.
3. El número `Ready=22s` se discute como "RTO del sistema" cuando en realidad es "tiempo hasta que k8s admite lo que ya pasó".

Además, el Deployment no declara `terminationGracePeriodSeconds`, así que el shutdown ordenado tiene los 30s default. Para el flush del offset al PVC (`/debezium/data/offsets.dat`) y cierre de la conexión al binlog en una sola operación de termination, 30s es suficiente en operación normal pero ajustado si hay GC pause o I/O lento. Subirlo a 60s da margen sin penalizar el caso normal (el grace period **no** se consume si el proceso termina antes).

Stakeholders: operador del lab, futura migración a producción.

**Aplicabilidad a producción:** todos los cambios de este change están en la categoría `production-relevant`. En el ambiente real (`mysql-primary`/`mysql-replica` fuera de Kubernetes), el bootstrap intrínseco de Debezium tarda lo mismo (JVM + Quarkus + conexión inicial), por lo que el calibrado de probes y el grace period se trasladan tal cual. El `initContainer` que esperaría a `mysql-replica` (Recomendación (d) del runbook de `evaluate-debezium-server-ha`) **no** se incluye aquí porque es `lab-only`: en producción la DB resuelve por DNS externo desde el primer instante.

## Goals / Non-Goals

**Goals:**
- Alinear `Ready=True` reportado por Kubernetes con la disponibilidad funcional real (~5–6s) medida en el change anterior.
- Asegurar que el shutdown del pod activo permita flush completo del offset al PVC.
- Verificar empíricamente la mejora re-ejecutando `minikube/scripts/rto_experiment.sh` y comparando con la baseline.

**Non-Goals:**
- Cambiar `replicas`, `strategy`, `resources`, ni la arquitectura del Deployment.
- Implementar HA activa/pasiva (lease, sidecar) — explícitamente descartado en `evaluate-debezium-server-ha`.
- Agregar `initContainer` o cualquier parche al race condition contra `mysql-replica` (`lab-only`, no aplica a producción).
- Tunear `livenessProbe`. Su `initialDelaySeconds: 30` actual ya tiene asimetría de riesgo a favor del conservadurismo (un kill prematuro por liveness es más costoso que un Ready demorado).
- Agregar `startupProbe`. Con `initialDelaySeconds=5` y `failureThreshold=3 + periodSeconds=10` en readiness, ya hay 30s de gracia para el bootstrap, suficiente para los ~5–6s observados con holgura amplia.

## Decisions

### Decisión 1 — `readinessProbe.initialDelaySeconds: 5`

**Elegido:** `5`. La medición observó `time-to-first-event` mediana de 5.52s (mysql8) y 6.11s (mysql57). Elegimos 5 (ligeramente por debajo del mínimo observado, 5.49s en mysql8) confiando en que `failureThreshold: 3 × periodSeconds: 10` provee una ventana de 30s adicional si el bootstrap se alarga. Concretamente, con esta config:

- t=0  delete → nuevo pod scheduled
- t≈1  contenedor inicia
- t≈5  Debezium emite primer evento, listener HTTP responde 200
- t=5  readiness probe arranca (initialDelaySeconds=5), primera evaluación → 200 → `Ready=True`

Resultado esperado: `time-to-Ready ≈ 7–8s` (que incluye scheduling, pull cacheado, y el delay+evaluación).

### Decisión 2 — `terminationGracePeriodSeconds: 60`

**Elegido:** `60`. El default de 30s funciona en condiciones normales, pero un GC pause o I/O lento puede dejar el flush a medias. 60s da el doble de margen sin costo en el caso normal (el grace period no se consume si el proceso termina antes). No vamos más alto porque un valor excesivo demora rollouts y drains.

### Decisión 3 — No tocar `livenessProbe`

`initialDelaySeconds: 30` es conservador a propósito. Un liveness kill prematuro durante un GC pause o un slow startup recrea todo el pod (no solo el contenedor con la misma identidad), perdiendo el warmup ganado. Como liveness no está en el camino de `Ready`, su valor no afecta el RTO medido y no hay incentivo para tocarlo.

### Decisión 4 — No agregar `startupProbe`

La latencia de bootstrap observada (~5–6s) ya cabe holgadamente en `readinessProbe.failureThreshold * periodSeconds = 30s`. Agregar `startupProbe` introduce complejidad sin beneficio. Si más adelante un nuevo conector requiere snapshot inicial (minutos), se reabre.

### Decisión 5 — Excluir `initContainer` para `mysql-replica`

El race condition de arranque contra `mysql-replica` que se observó en `evaluate-debezium-server-ha` (1–5 restarts en cold start del cluster) es **específico del lab**: solo ocurre porque `mysql-replica` es un Pod del mismo cluster. En el ambiente real la DB vive fuera de Kubernetes y su hostname resuelve siempre. Agregar un `initContainer` aquí introduciría divergencia entre lab y prod, lo cual:

1. Hace que el lab no reproduzca fielmente el comportamiento de prod (la métrica de cold-start del lab dejaría de ser un proxy útil para diagnosticar problemas reales).
2. Crea un manifest "del lab" distinto al "de prod", duplicando la superficie a mantener.

Se documenta como `lab-only` y queda fuera del alcance.

### Decisión 6 — Verificación empírica obligatoria antes de archivar

Tras aplicar los manifests modificados, se re-ejecuta `minikube/scripts/rto_experiment.sh` para confirmar que `time-to-Ready` baja al rango esperado (~7–8s) y que `time-to-first-event` se mantiene (~5–6s, sin regresión). Si la mejora medida no se materializa o aparece regresión, este change debe reabrir su Decisión 1 antes de archivar.

## Risks / Trade-offs

- **[Riesgo] `initialDelaySeconds: 5` puede ser demasiado agresivo si una imagen futura tarda más en arrancar.** Mitigación: `failureThreshold: 3 × periodSeconds: 10` da 30s adicionales antes de que k8s considere el pod NotReady. Es decir, el pod tiene hasta 35s de bootstrap antes de que la probe fracase definitivamente, lo cual cubre 6x el bootstrap mediano observado.
- **[Riesgo] `terminationGracePeriodSeconds: 60` ralentiza rollouts si el pod no responde a SIGTERM y k8s tiene que esperar el período completo.** Mitigación: en la práctica Debezium responde a SIGTERM y termina el flush en pocos segundos; el grace period solo se consume completo en escenarios patológicos.
- **[Riesgo] El re-experimento puede revelar que la mejora es menor a la esperada (por ejemplo, scheduling latency mayor en la prueba).** Mitigación: el experimento se ejecuta 3 veces por stack; si la mediana de `time-to-Ready` no baja al menos 10s respecto a la baseline, reabrir Decisión 1.
- **[Trade-off] No cerrar el problema del race condition de arranque en el lab.** Aceptado: el cold-start del lab seguirá mostrando 1–5 restarts hasta que `mysql-replica` esté Ready. Es ruido conocido y documentado.

## Migration Plan

1. Aplicar el manifest de cada stack con `kubectl apply -f`. `strategy: Recreate` causa una breve ventana de indisponibilidad por stack — la misma ventana que ya se acepta en `evaluate-debezium-server-ha`.
2. Esperar `kubectl rollout status deployment/debezium-server -n <ns>` en ambos stacks.
3. Re-ejecutar `minikube/scripts/rto_experiment.sh` (3 corridas por stack).
4. Comparar la mediana observada contra la baseline (22.16–22.24s). Si la nueva mediana es < 10s, dar por confirmada la Decisión 1.
5. Anotar resultados en `runbook.md` (sección "Verificación post-hardening") y proceder a archivar.

## Open Questions

- ¿La calibración elegida (`initialDelaySeconds: 5`) se sostiene si el sink CDC futuro tarda más en aceptar la primera conexión HTTP? Hoy `cdc-sink` responde casi instantáneamente; si en algún momento se reemplaza por algo más pesado, reabrir.
- ¿`terminationGracePeriodSeconds: 60` es suficiente bajo `kubectl drain` con muchos pods? Para este lab (un solo pod por stack, un solo nodo) la respuesta es trivialmente sí. Para multi-nodo futuro, revisar.
