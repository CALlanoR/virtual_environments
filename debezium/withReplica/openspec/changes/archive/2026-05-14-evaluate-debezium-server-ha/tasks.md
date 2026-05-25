## 1. Auditoría de la configuración actual

- [x] 1.1 Leer `minikube/mysql5.7/06-debezium-server.yaml` y `minikube/mysql8/06-debezium-server.yaml` y registrar en `design.md` (sección nueva "Estado actual" al inicio): `replicas`, `strategy.type`, presencia/ausencia de `livenessProbe`/`readinessProbe`/`startupProbe`, `terminationGracePeriodSeconds`, `resources`, `mountPath` del PVC `debezium-data`, imagen.
- [x] 1.2 En ambos `01-configmaps.yaml`, verificar que `offset.storage.file.filename` y `schema.history.internal.file.filename` apuntan a un path dentro del `mountPath` del PVC `debezium-data`. Anotar en `design.md` cualquier ruta que caiga fuera.

## 2. Probes mínimas para hacer Ready observable

- [x] 2.1 Identificar qué sonda concreta usar en cada imagen (`debezium/server:2.4.2.Final` y `withreplica/debezium-server-mysql:3.5.0.Final`). Probar `kubectl exec` para descubrir si responde HTTP `/q/health` o si hay que caer a TCP/`exec`. Anotar en `design.md` la decisión por imagen y resolver la Open Question 1.
- [x] 2.2 Modificar `minikube/mysql5.7/06-debezium-server.yaml` añadiendo `livenessProbe` y `readinessProbe` con los valores de la Decisión 1 del design.
- [x] 2.3 Modificar `minikube/mysql8/06-debezium-server.yaml` con las mismas probes adaptadas a la imagen.
- [x] 2.4 Aplicar ambos manifests (`kubectl apply -f ...`) y confirmar que los dos pods llegan a `Ready=True` con las probes activas.

## 3. Medición — stack `cdc-mysql8`

- [x] 3.1 Asegurar que `minikube/load-generator/` está corriendo y emitiendo escrituras al primary del stack 8.
- [x] 3.2 Iniciar un watch en paralelo: `kubectl get pods -n cdc-mysql8 -l app=debezium-server -w -o wide` (o con `jsonpath` sobre `status.conditions`) para capturar la transición a `Ready=True` con timestamp.
- [x] 3.3 Iniciar consumo del sink (`kubectl logs -f ...` del sink o `kubectl exec` sobre el contenedor receptor) capturando timestamps del último evento previo y de cada evento siguiente.
- [x] 3.4 Ejecutar `kubectl delete pod -l app=debezium-server -n cdc-mysql8 --grace-period=0 --force` registrando `t_delete`.
- [x] 3.5 Cronometrar `time-to-Ready` (3.2) y `time-to-first-event` (3.3) del pod sustituto.
- [x] 3.6 Repetir 3.4–3.5 al menos 3 veces (5 si la dispersión max/min supera 2x la mediana). Registrar (mín, mediana, máx) de ambas métricas en `design.md`.

## 4. Medición — stack `cdc-mysql57`

- [x] 4.1 Repetir 3.1–3.6 contra el stack `cdc-mysql57`.
- [x] 4.2 Anotar en `design.md` las diferencias frente al stack 8 (imagen, bootstrap time, gap entre `Ready` y `first-event`).

## 5. Documentación del proceso

- [x] 5.1 Crear `openspec/changes/evaluate-debezium-server-ha/runbook.md` con una bitácora paso a paso del experimento, ordenada cronológicamente y reproducible por otra persona sin contexto previo. Debe cubrir desde el setup hasta el cierre.
- [x] 5.2 Para cada paso ejecutado en las tasks 1–4, registrar en `runbook.md`: el comando exacto invocado (con namespace y flags), un resumen del output relevante (no pegar logs completos; sí pegar las líneas clave con timestamps), y el resultado observado.
- [x] 5.3 Incluir en `runbook.md` una tabla resumen con las corridas de medición: por stack, número de corrida, `t_delete`, `time-to-Ready`, `time-to-first-event` y cualquier observación (p. ej. corrida descartada por reinicio del load-generator).
- [x] 5.4 Agregar al final de `runbook.md` una sección **Recomendaciones** con: (a) sonda definitiva sugerida por imagen, (b) si el gap `Ready` vs `first-event` justifica `startupProbe` o probe más estricta, (c) si el RTO observado motiva abrir el change de hardening, (d) cualquier mejora colateral detectada durante el experimento (logs ruidosos, defaults engañosos, etc.). Si no hay recomendaciones, dejar la sección con "Ninguna; la configuración actual cumple lo medido" para que la ausencia sea explícita.

## 6. Cierre

- [x] 6.1 Verificar que el consumidor del sink no reportó eventos duplicados respecto al offset previo al delete en ninguna corrida (cumple Requirement: No-duplicación tras recuperación).
- [x] 6.2 Actualizar la sección Open Questions de `design.md` con los hallazgos (sonda elegida, gap `Ready` vs `first-event` observado, recomendación sobre si abrir un change de hardening). Las recomendaciones detalladas viven en `runbook.md`; aquí solo se resume el resultado.
- [x] 6.3 Ejecutar `openspec validate evaluate-debezium-server-ha --strict` y corregir errores de formato.
- [x] 6.4 Si las recomendaciones de 5.4 motivan hardening adicional (tuning de probes, `startupProbe`, `terminationGracePeriodSeconds`, etc.), abrir un change posterior. No hacerlo aquí. **Hecho:** se creó `openspec/changes/harden-debezium-server-restart/` con scope acotado a las recomendaciones `production-relevant` (a, b, c, e); la recomendación (d) sobre `initContainer` se excluye explícitamente por ser `lab-only`.
