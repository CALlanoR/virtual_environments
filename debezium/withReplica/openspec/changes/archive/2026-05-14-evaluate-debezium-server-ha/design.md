## Estado actual

Auditoría de los manifests al `2026-05-14` (commit `97d94bb`). Ambos stacks son estructuralmente idénticos salvo imagen y `mountPath` del ConfigMap:

| Campo | `cdc-mysql57` | `cdc-mysql8` |
|---|---|---|
| `spec.replicas` | `1` | `1` |
| `spec.strategy.type` | `Recreate` | `Recreate` |
| `livenessProbe` | ausente | ausente |
| `readinessProbe` | ausente | ausente |
| `startupProbe` | ausente | ausente |
| `terminationGracePeriodSeconds` | no declarado (default 30s) | no declarado (default 30s) |
| `resources.requests` | `memory: 512Mi`, `cpu: 200m` | `memory: 512Mi`, `cpu: 200m` |
| `resources.limits` | `memory: 1Gi`, `cpu: 1000m` | `memory: 1Gi`, `cpu: 1000m` |
| Imagen | `debezium/server:2.4.2.Final` | `withreplica/debezium-server-mysql:3.5.0.Final` |
| PVC | `debezium-data`, `ReadWriteOnce`, `100Mi` | `debezium-data`, `ReadWriteOnce`, `100Mi` |
| PVC `mountPath` | `/debezium/data` | `/debezium/data` |
| ConfigMap mount | `/debezium/conf` (readOnly) | `/debezium/config` (readOnly) |
| `offset.storage.file.filename` | `/debezium/data/offsets.dat` (dentro del PVC ✓) | `/debezium/data/offsets.dat` (dentro del PVC ✓) |
| `schema.history.internal.file.filename` | `/debezium/data/schema-history.dat` (dentro del PVC ✓) | `/debezium/data/schema-history.dat` (dentro del PVC ✓) |

**Hallazgo colateral observado en `kubectl describe` del lab corriendo antes de empezar el experimento:**
- `cdc-mysql8/debezium-server` acumula `RESTARTS=5` con `Last State: Terminated/Completed/Exit Code 0` y logs `Communications link failure` apuntando a `mysql-replica`.
- `cdc-mysql57/debezium-server` acumula `RESTARTS=1` con `UnknownHostException: mysql-replica: Name or service not known`.

Ambos son race conditions de arranque entre Debezium y `mysql-replica` (Service/DNS no propagado y/o réplica todavía no aceptando conexiones). El Deployment carece de `initContainer` o probe que espere a `mysql-replica`. Esto es ruido relevante para la medición y motiva la Decisión 6.

## Context

El laboratorio `withReplica/` despliega en minikube dos stacks paralelos (`cdc-mysql57` y `cdc-mysql8`). Cada stack contiene un Deployment `debezium-server` cuya configuración actual (verificada en los manifests) es:

- `replicas: 1`
- `strategy.type: Recreate`
- Un único contenedor (`debezium/server:2.4.2.Final` en 5.7, `withreplica/debezium-server-mysql:3.5.0.Final` en 8) con `requests: 512Mi/200m`, `limits: 1Gi/1000m`.
- Volumen `debezium-data` montado en `/debezium/data` (PVC `ReadWriteOnce`, 100Mi). Persiste offset y schema history.
- ConfigMap `debezium-config` montado en `/debezium/conf` (5.7) o `/debezium/config` (8.0), modo `readOnly`.
- **Sin** `livenessProbe`, **sin** `readinessProbe`, **sin** `startupProbe`.
- **Sin** `terminationGracePeriodSeconds` explícito (default 30s).

Sin probes, el `Ready=True` que reporta `kubectl` significa solamente "el contenedor está corriendo" — no garantiza que Debezium haya completado el bootstrap, abierto la conexión de replicación al binlog y empezado a emitir eventos. Por eso la medición tiene que distinguir entre la señal de Kubernetes y la señal funcional end-to-end.

Stakeholders: operador del lab (rol de SRE-en-prácticas), lectura del sink CDC para verificar reanudación.

## Resultados de la medición

Ejecutado `2026-05-14` con `/tmp/rto_measure.py`. 3 corridas por stack, warmup de 60s, load-generator activo con `--interval 0.5 --duration 1200`. Métrica `time-to-first-event` calculada filtrando eventos del sink por IP del pod sustituto (las corridas previas sin filtro de IP captaban eventos en vuelo del pod viejo y daban resultados artificialmente bajos en mysql5.7; esa metodología fue corregida y los números reportados aquí son los del filtro de IP).

| Stack | time-to-Ready (min / mediana / máx) | time-to-first-event (min / mediana / máx) |
|---|---|---|
| `cdc-mysql8` (`withreplica/debezium-server-mysql:3.5.0.Final`) | 21.93 / 22.24 / 22.33 s | 5.49 / 5.52 / 5.55 s |
| `cdc-mysql57` (`debezium/server:2.4.2.Final`) | 22.04 / 22.16 / 22.41 s | 6.00 / 6.11 / 6.11 s |

**Diferencias entre stacks:** despreciables. Ambas imágenes tardan ~5–6s en empezar a emitir eventos tras el delete, y ~22s en ser marcadas `Ready` por Kubernetes. mysql5.7 (imagen `2.4.2.Final`) es ~0.5s más lenta en `time-to-first-event` que mysql8 (`3.5.0.Final`), por debajo del ruido entre corridas.

**Gap `time-to-Ready` vs `time-to-first-event` ≈ 16s en ambos stacks.** Es decir: el pod sustituto ya está sirviendo CDC funcional ~16s antes de que `kubectl get pods` reporte `Ready=True`. Esto no es un problema de Debezium sino del valor `readinessProbe.initialDelaySeconds: 20` que fijamos en la Decisión 1. Como `initialDelaySeconds` se cuenta desde el arranque del contenedor (~0s después del scheduling), y la primera evaluación de la sonda ocurre a +20s (luego `periodSeconds: 10`), el `Ready` empírico es `initialDelaySeconds` + jitter de la primera evaluación + tiempo de scheduling ≈ 22s. Se discute en Recomendaciones de `runbook.md`.

**No-duplicación:** durante las 12 corridas totales (3 + 3 con metodología v1 + 3 + 3 con metodología v2), el sink no reportó eventos cuyo offset fuera ≤ al último confirmado antes del delete; Debezium reanudó limpiamente desde el offset persistido en el PVC `debezium-data`.

**Aplicabilidad a producción:** este lab es un ambiente de prueba. En el ambiente real, `mysql-primary` y `mysql-replica` **no** corren en Kubernetes; la base de datos vive fuera del cluster y se asume siempre disponible. Esto importa para distinguir recomendaciones que se trasladan a producción de las que son artefactos del lab. El detalle por recomendación está etiquetado como `Production-relevant` o `Lab-only` en `runbook.md` sección 7. Resumen:
- Tiempo de bootstrap intrínseco de Debezium (~5–6s) y calibración de probes: **production-relevant**.
- Race condition de arranque contra el Service `mysql-replica` y la sugerencia de `initContainer`: **lab-only** (en producción la DB no es un Pod de k8s).

## Goals / Non-Goals

**Goals:**
- Medir empíricamente el tiempo de recuperación del Deployment `debezium-server` tras la caída del pod activo, en ambos stacks.
- Reportar dos métricas independientes: `time-to-Ready` (recovery de Kubernetes) y `time-to-first-event` (disponibilidad funcional).
- Hacer la señal de `Ready` confiable agregando probes mínimas antes de medir.

**Non-Goals:**
- Evaluar o implementar estrategias activas/pasivas, leases, sidecars, ni cambios estructurales al Deployment más allá de las probes mínimas.
- Tunear las probes con valores definitivos. Solo se ponen valores razonables para que la métrica de `Ready` sea útil; un change posterior puede ajustarlos.
- Cubrir HA de MySQL primary/replica.
- Medir bajo condiciones distintas a `kubectl delete pod` (no se cubren eviction de nodo, OOMKill ni drain).
- Comparar imágenes (`2.4.2.Final` vs `3.5.0.Final`) como objetivo; las diferencias se reportan pero no se buscan.

## Decisions

### Decisión 1 — Agregar probes mínimas antes de medir

**Elegido:** añadir a ambos Deployments un `livenessProbe` y un `readinessProbe`. La sonda exacta se decide en la Task 2.1 según lo que expone cada imagen (HTTP `/q/health` si está disponible; si no, TCP al puerto de management o `exec` con un check sobre el proceso). Valores conservadores iniciales:

- `livenessProbe`: `initialDelaySeconds: 30`, `periodSeconds: 15`, `failureThreshold: 4`.
- `readinessProbe`: `initialDelaySeconds: 20`, `periodSeconds: 10`, `failureThreshold: 3`.

**Razón:** sin probes, `Ready=True` solo indica que el contenedor arrancó. Eso no distingue "Kubernetes recreó el pod" de "Debezium ya está consumiendo el binlog", y ambas son interesantes pero distintas. La readiness probe hace que `Ready` se acerque a la segunda. La medición sin probes sería estructuralmente ambigua.

No se elige liveness más agresiva ni se suma `startupProbe`. Ese tuning es un change derivado, condicionado al resultado de la medición.

### Decisión 2 — Reportar dos métricas independientes

- **time-to-Ready**: intervalo entre `t_delete` y la transición a `Ready=True` del pod sustituto, observada vía `kubectl get pods -w`. Mide latencia de Kubernetes (scheduler + pull cacheado + arranque del contenedor + readiness probe satisfecha).
- **time-to-first-event**: intervalo entre `t_delete` y el primer evento CDC nuevo recibido en el sink tras el pod sustituto. Mide latencia funcional end-to-end (Ready + bootstrap interno de Debezium hasta reanudar el binlog).

Reportarlas por separado permite saber cuánto del RTO es responsabilidad de Kubernetes y cuánto del propio proceso de Debezium. Si el gap entre ambas es grande, indica que la readiness probe está permitiendo `Ready` antes de que el conector realmente esté trabajando, y se debería revisar la sonda en un change posterior.

### Decisión 3 — Inyección de fallo simple y reproducible

Se usa `kubectl delete pod -l app=debezium-server -n <ns> --grace-period=0 --force`. Es el equivalente más cercano a un crash inesperado, no depende de simular eviction o OOMKill, y es trivial de repetir. Otros modos de fallo quedan fuera del alcance.

### Decisión 4 — N mínimo de corridas y reporte

Mínimo 3 corridas por stack. Se reporta (mín, mediana, máx) de cada métrica. Si la dispersión max/min de cualquiera de las dos métricas supera 2x la mediana, se amplía a 5 corridas para reducir el ruido antes de archivar el change.

### Decisión 6 — Calentamiento de 60s antes de cada corrida

Antes de cada `kubectl delete pod` para medir, el pod activo de `debezium-server` SHALL llevar al menos **60 segundos consecutivos** en `Ready=True` con `RESTARTS` sin incrementar. Esto evita que el race condition de arranque contra `mysql-replica` (ver "Estado actual") contamine la métrica `time-to-Ready`: si midiéramos sobre un pod que todavía está en su ventana de retry inicial, el sustituto post-delete probablemente reiniciaría 1–5 veces antes de quedar Ready, y el RTO observado mezclaría dos problemas distintos. El warmup separa el experimento (RTO de recovery) del bug de bootstrap (que se documenta como hallazgo, no se arregla aquí).

### Decisión 5 — Generar carga durante la medición

El stack `minikube/load-generator/` debe estar activo durante las corridas, para que el sink reciba eventos de forma continua y la marca de "primer evento tras la caída" sea inequívoca. Sin carga continua no se puede medir `time-to-first-event` con precisión: habría que esperar a que algún proceso humano escriba en la fuente.

## Risks / Trade-offs

- **[Riesgo] La sonda elegida puede no reflejar fielmente el estado real del conector.** Si la imagen no expone un endpoint de salud específico, una sonda TCP/`exec` puede dar `Ready` antes de que el binlog reanude. Mitigación: la métrica `time-to-first-event` detecta exactamente este caso; si el gap es grande respecto a `time-to-Ready`, se documenta y se abre un change para mejorar la sonda.
- **[Riesgo] Diferencias entre las imágenes (`2.4.2.Final` vs `3.5.0.Final`) hacen que las dos mediciones no sean directamente comparables.** Aceptado: el objetivo no es comparar imágenes sino caracterizar cada stack tal como está hoy.
- **[Trade-off] Agregar probes es un cambio de manifest, no solo evaluación.** El alcance original era no tocar manifests. Se acepta tocarlos lo mínimo (solo probes, sin cambiar replicas/strategy/resources) porque sin esa señal la medición no sería útil.
- **[Riesgo] `strategy: Recreate` provoca una ventana de indisponibilidad al aplicar las probes.** Aceptado: ventana corta, esperada, no requiere coordinación.

## Migration Plan

Aplicar los manifests modificados con `kubectl apply -f minikube/mysql5.7/06-debezium-server.yaml` y `kubectl apply -f minikube/mysql8/06-debezium-server.yaml`. Como `strategy: Recreate`, habrá una breve ventana de indisponibilidad en cada stack al aplicar el cambio; esto es esperado. Las probes se pueden retirar sin impacto en el resto del lab si la medición se descarta.

## Open Questions

- ~~¿Qué sonda exacta expone cada imagen?~~ **Resuelto (`2026-05-14`):** ambas imágenes son Quarkus y exponen los endpoints standard en puerto `8080`. Sonda: `httpGet /q/health/live` (liveness) y `httpGet /q/health/ready` (readiness). Verificado con `curl` → HTTP 200 en ambos pods.
- ¿Cuál es el RTO máximo que el lab considera aceptable? Sigue sin formalizar. Para referencia, lo medido: `time-to-first-event ≈ 5–6s`, `time-to-Ready ≈ 22s`. Un change posterior puede fijar un umbral con estos números como baseline.
- ~~¿El gap observado entre `time-to-Ready` y `time-to-first-event` justifica una probe de salud más estricta o un `startupProbe`?~~ **Resuelto (`2026-05-14`):** el gap es de ~16s y está dominado por `readinessProbe.initialDelaySeconds: 20`. **No** se justifica `startupProbe`; **sí** se justifica bajar `initialDelaySeconds` a 5s en un change posterior. Detalles en `runbook.md` sección Recomendaciones (b).
- **Nuevo hallazgo:** el bootstrap inicial de Debezium (cuando el cluster arranca en frío) sufre race condition contra el Service `mysql-replica` (DNS / conexión), causando 1–5 restarts antes de quedar Ready. No afecta el RTO post-warmup pero sí ensucia el arranque del lab. Recomendación: `initContainer` que espere a `mysql-replica` — `runbook.md` sección Recomendaciones (d).
