> **Status: NOT IMPLEMENTED — archivado el 2026-05-14.**
>
> Esta propuesta se generó como follow-up de `evaluate-debezium-server-ha` y quedó archivada **sin implementar**. La decisión del operador fue dejar la configuración del lab como estaba al final del change anterior (probes con `initialDelaySeconds: 20`, sin `terminationGracePeriodSeconds`), porque para el caso de uso actual el RTO observado (`time-to-first-event ≈ 5–6s`, `time-to-Ready ≈ 22s`) ya cumple y el costo operativo de tocar manifests no se justifica hoy.
>
> El razonamiento técnico (qué cambios harían falta, por qué excluimos el `initContainer`, qué probar después) queda preservado por si en algún momento se decide retomarlo. Para reabrir: leer este `proposal.md` + `design.md` + las recomendaciones del `runbook.md` del change archivado `2026-05-14-evaluate-debezium-server-ha`.

## Why

El change `evaluate-debezium-server-ha` midió empíricamente que la configuración actual del Deployment `debezium-server` recupera funcionalidad CDC en **~5–6s** tras un kill forzado, pero Kubernetes no marca `Ready=True` hasta **~22s** después. El gap (~16s) está dominado por `readinessProbe.initialDelaySeconds: 20`, un valor conservador que elegimos antes de medir. Adicionalmente, el Deployment no declara `terminationGracePeriodSeconds`, lo que en un shutdown ordenado puede no dar tiempo suficiente a Debezium para flushear el offset al PVC.

Las recomendaciones (a), (b), (c) y la auxiliar sobre `terminationGracePeriodSeconds` del `runbook.md` del change anterior están etiquetadas como **`production-relevant`**: aplican tanto al lab como al ambiente real, donde la base de datos vive fuera de Kubernetes. La recomendación (d) sobre un `initContainer` que espere a `mysql-replica` está etiquetada como **`lab-only`** y **se excluye explícitamente** de este change para no introducir divergencia entre la config del lab y la de producción.

## What Changes

- Bajar `readinessProbe.initialDelaySeconds` de `20` a `5` en ambos manifests (`minikube/mysql5.7/06-debezium-server.yaml` y `minikube/mysql8/06-debezium-server.yaml`), alineando el `Ready=True` reportado por Kubernetes con la disponibilidad funcional real medida.
- Declarar `terminationGracePeriodSeconds: 60` en ambos Deployments, para que el shutdown ordenado de Debezium pueda flushear el offset (`/debezium/data/offsets.dat`) y cerrar la conexión al binlog sin truncamiento.
- Mantener `livenessProbe` con los valores actuales (`initialDelaySeconds: 30`, `periodSeconds: 15`, `failureThreshold: 4`). No agregar `startupProbe` (Recomendación (c) del runbook).
- Re-ejecutar el experimento de `evaluate-debezium-server-ha` con la nueva configuración usando `minikube/scripts/rto_experiment.sh` y verificar que `time-to-Ready` baja a ~7–8s, alineándose con `time-to-first-event` (~5–6s).
- **No** se agrega `initContainer` ni ningún otro parche relacionado al race condition de arranque contra `mysql-replica`; ese problema solo existe en el lab y no en el ambiente real (`mysql-primary`/`mysql-replica` viven fuera de Kubernetes en producción).

## Capabilities

### Modified Capabilities
- `debezium-server-ha`: se refinan los requirements de probes para fijar `initialDelaySeconds` calibrado empíricamente, y se agrega un requirement de terminación ordenada con grace period suficiente para flush del offset.

## Impact

- **Manifests Kubernetes:** `minikube/mysql5.7/06-debezium-server.yaml` y `minikube/mysql8/06-debezium-server.yaml` se modifican (sólo `readinessProbe.initialDelaySeconds` y `terminationGracePeriodSeconds`). `replicas`, `strategy`, `livenessProbe`, `resources` y el PVC no cambian.
- **Documentación / specs:** se MODIFICA el Requirement "Probes mínimas presentes en ambos manifests" de la capability `debezium-server-ha` para fijar el valor calibrado de `readinessProbe.initialDelaySeconds`. Se AGREGA un Requirement "Terminación ordenada con grace period suficiente" a la misma capability.
- **Operación:** `kubectl apply -f` de ambos manifests genera una breve ventana de indisponibilidad por `strategy: Recreate` (esperado, mismo comportamiento que el change anterior).
- **Dependencias externas:** ninguna. La imagen de Debezium ya expone los endpoints `/q/health/{live,ready}` que las probes usan; no hace falta upgrade ni rebuild.

## Dependencies

Este change depende de que `evaluate-debezium-server-ha` esté archivado o aplicado, porque MODIFICA un Requirement introducido en aquél. Si se aplica antes del archivo del change anterior, la validación de OpenSpec debe ejecutarse contra ambos en orden (`evaluate` primero, luego `harden`).
