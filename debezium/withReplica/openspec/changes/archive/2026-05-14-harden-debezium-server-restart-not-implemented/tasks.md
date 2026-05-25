## 1. Pre-condición

- [ ] 1.1 Confirmar que `evaluate-debezium-server-ha` está archivado o aplicado (sus manifests con probes ya están en `minikube/mysql{5.7,8}/06-debezium-server.yaml`). Si no, completar y archivar primero ese change.
- [ ] 1.2 Confirmar que `minikube/scripts/rto_experiment.sh` existe y es ejecutable (lo introdujo el change anterior). Ejecutar un dry-run inocuo (`bash -n minikube/scripts/rto_experiment.sh`).

## 2. Modificación de manifests

- [ ] 2.1 En `minikube/mysql5.7/06-debezium-server.yaml`:
  - Bajar `readinessProbe.initialDelaySeconds` de `20` a `5`.
  - Agregar `spec.template.spec.terminationGracePeriodSeconds: 60` (al mismo nivel que `containers:` y `volumes:`).
- [ ] 2.2 En `minikube/mysql8/06-debezium-server.yaml`: aplicar los mismos dos cambios.
- [ ] 2.3 No tocar `livenessProbe`, no agregar `startupProbe`, no agregar `initContainer`. Verificar con `git diff -- minikube/mysql{5.7,8}/06-debezium-server.yaml` que el diff es estrictamente acotado.

## 3. Aplicación y verificación funcional

- [ ] 3.1 `kubectl apply -f minikube/mysql5.7/06-debezium-server.yaml` y `kubectl apply -f minikube/mysql8/06-debezium-server.yaml`.
- [ ] 3.2 `kubectl rollout status deployment/debezium-server -n cdc-mysql8 --timeout=180s` y lo mismo para `cdc-mysql57`. Ambos pods deben quedar `Ready=1/1` con `RESTARTS` sin incrementar respecto al estado pre-apply.
- [ ] 3.3 `kubectl get deployment debezium-server -n cdc-mysql8 -o jsonpath='{.spec.template.spec.terminationGracePeriodSeconds}'` debe devolver `60`. Idem para `cdc-mysql57`.
- [ ] 3.4 `kubectl get deployment debezium-server -n cdc-mysql8 -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.initialDelaySeconds}'` debe devolver `5`. Idem para `cdc-mysql57`.

## 4. Re-medición con el script automatizado

- [ ] 4.1 Ejecutar `minikube/scripts/rto_experiment.sh 3` (3 corridas por stack).
- [ ] 4.2 Capturar los CSV y la tabla de resumen que imprime el script.
- [ ] 4.3 Comparar la nueva mediana de `time_to_ready_seconds` contra la baseline (22.16s mysql57, 22.24s mysql8 del change anterior). Esperado: caída a ~7–8s (mejora ≥ 14s).
- [ ] 4.4 Comparar la nueva mediana de `time_to_first_event_seconds` contra la baseline (6.11s mysql57, 5.52s mysql8). Esperado: sin cambio significativo (±0.5s).

## 5. Documentación

- [ ] 5.1 Agregar a `openspec/changes/evaluate-debezium-server-ha/runbook.md` (si no se ha archivado aún) o a un `runbook.md` propio de este change una sección "Verificación post-hardening" con la tabla nueva vs baseline.
- [ ] 5.2 Si la mejora medida es menor a la esperada (`time-to-Ready` mediana > 12s), no archivar este change. Reabrir Decisión 1 del design y ajustar `initialDelaySeconds` con datos nuevos.
- [ ] 5.3 Si la mejora se confirma, anotar en `design.md` (sección "Resultados de verificación") los nuevos valores observados.

## 6. Cierre

- [ ] 6.1 Verificar que el consumidor del sink no reportó eventos duplicados durante el re-experimento (sigue cumpliendo el Requirement "No-duplicación tras recuperación" heredado).
- [ ] 6.2 `openspec validate harden-debezium-server-restart --type change --strict` y corregir cualquier error de formato.
- [ ] 6.3 Marcar listo para archivar.
