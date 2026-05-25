## Why

Hoy el Deployment `debezium-server` en minikube (stacks `cdc-mysql57` y `cdc-mysql8`) corre con `replicas: 1`, `strategy: Recreate` y **sin** probes de liveness/readiness. Si el pod se cae (crash, eviction, delete manual), no sabemos con datos cuánto tarda Kubernetes en levantarlo ni cuánto pasa hasta que Debezium vuelve a emitir eventos al sink. Antes de tomar cualquier decisión de hardening adicional, necesitamos **medir el comportamiento real** de la configuración actual en ambos stacks.

## What Changes

- Auditar la configuración actual del Deployment `debezium-server` en `minikube/mysql5.7/06-debezium-server.yaml` y `minikube/mysql8/06-debezium-server.yaml` (replicas, strategy, probes, resources, PVC).
- Agregar probes mínimas (`livenessProbe` + `readinessProbe`) a ambos manifests para que `Ready=True` sea una señal útil. Sin esas probes, `Ready` solo refleja que el contenedor arrancó, no que Debezium ya esté consumiendo el binlog.
- Inyectar fallos del pod activo en ambos stacks (`kubectl delete pod ... --grace-period=0 --force`) y medir **dos métricas por separado**:
  - **time-to-Ready**: tiempo entre el delete y `Ready=True` del pod sustituto.
  - **time-to-first-event**: tiempo entre el delete y el primer evento CDC emitido por el pod sustituto al sink.
- Documentar resultados (mín, mediana, máx de al menos 3 corridas por stack) y registrar el gap entre ambas métricas, que es lo que diferencia "Kubernetes recreó el pod" de "Debezium volvió a trabajar".
- No se evalúan estrategias alternativas de HA (active/passive, leases, sidecars) en este change. Si la medición motiva hardening adicional, se propondrá como change posterior.

## Capabilities

### New Capabilities
- `debezium-server-ha`: Evaluación empírica del tiempo de recuperación de Debezium en minikube tras la caída del pod activo, con probes mínimas que hacen observable la disponibilidad y métricas separadas de Ready y de primer evento.

### Modified Capabilities
<!-- Ninguna. Este change introduce una capability nueva de evaluación; la capability existente `mysql-replica-debezium-k8s` solo se referencia, no cambia sus requirements. -->

## Impact

- **Manifests Kubernetes:** `minikube/mysql5.7/06-debezium-server.yaml` y `minikube/mysql8/06-debezium-server.yaml` se modifican para añadir `livenessProbe` y `readinessProbe`. No cambia `replicas`, `strategy`, `resources`, ni el PVC.
- **Documentación / specs:** se agrega la capability `debezium-server-ha` bajo `openspec/specs/` con requirements observables sobre presencia de probes y reporte de las dos métricas.
- **Operación:** ninguna fuera del lab. La medición se ejecuta contra el cluster minikube local, con `minikube/load-generator/` activo para asegurar tráfico continuo durante el experimento.
- **Dependencias externas:** ninguna.
