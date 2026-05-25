## ADDED Requirements

### Requirement: Configuración actual bajo evaluación

El Deployment `debezium-server` en ambos stacks (`cdc-mysql57` y `cdc-mysql8`) SHALL declarar `spec.replicas: 1` y `spec.strategy.type: Recreate`. Esta es la configuración cuyo comportamiento de recuperación se evalúa en este change; cualquier desviación invalida los resultados de la medición.

#### Scenario: replicas=1 y strategy Recreate en stack 5.7
- **WHEN** se inspecciona `minikube/mysql5.7/06-debezium-server.yaml`
- **THEN** el Deployment `debezium-server` declara `spec.replicas: 1` y `spec.strategy.type: Recreate`

#### Scenario: replicas=1 y strategy Recreate en stack 8
- **WHEN** se inspecciona `minikube/mysql8/06-debezium-server.yaml`
- **THEN** el Deployment `debezium-server` declara `spec.replicas: 1` y `spec.strategy.type: Recreate`

### Requirement: Probes mínimas presentes en ambos manifests

El Deployment `debezium-server` SHALL declarar al menos `livenessProbe` y `readinessProbe` en ambos stacks, con valores conformes a la Decisión 1 de `design.md` (o equivalentes), de modo que `Ready=True` refleje que Debezium completó el bootstrap y no solo que el contenedor arrancó.

#### Scenario: livenessProbe y readinessProbe en stack 5.7
- **WHEN** se inspecciona el contenedor principal en `minikube/mysql5.7/06-debezium-server.yaml`
- **THEN** el contenedor declara `livenessProbe` y `readinessProbe`

#### Scenario: livenessProbe y readinessProbe en stack 8
- **WHEN** se inspecciona el contenedor principal en `minikube/mysql8/06-debezium-server.yaml`
- **THEN** el contenedor declara `livenessProbe` y `readinessProbe`

### Requirement: Durabilidad del offset y schema history

El Deployment `debezium-server` SHALL montar un PersistentVolumeClaim `ReadWriteOnce` que persiste el offset del binlog y el archivo de historial de schemas, para que el pod sustituto reanude desde el último offset confirmado y no provoque re-snapshot completo ni emita eventos duplicados al sink.

#### Scenario: PVC declarado en ambos stacks
- **WHEN** se inspeccionan los manifests de Debezium en `minikube/mysql5.7/` y `minikube/mysql8/`
- **THEN** existe un `PersistentVolumeClaim` `debezium-data` con `accessModes: ["ReadWriteOnce"]` montado en el path donde Debezium escribe offset y history

#### Scenario: Rutas de offset y history dentro del PVC
- **WHEN** se inspeccionan los ConfigMaps `debezium-config` de ambos stacks
- **THEN** `offset.storage.file.filename` y `schema.history.internal.file.filename` apuntan a paths dentro del `mountPath` del PVC `debezium-data`

### Requirement: Recuperación medida tras caída del pod activo

Cuando el pod activo de `debezium-server` se elimina con `kubectl delete pod ... --grace-period=0 --force`, el Deployment controller SHALL recrear un pod sustituto que monta el mismo PVC y reanuda el consumo del binlog sin intervención manual. El change SHALL reportar, para cada stack, dos métricas separadas: `time-to-Ready` y `time-to-first-event`.

#### Scenario: El pod se recrea sin intervención
- **WHEN** se ejecuta `kubectl delete pod -l app=debezium-server -n <ns> --grace-period=0 --force` en cualquiera de los stacks
- **THEN** un nuevo pod con el mismo label aparece en estado `Ready=True` sin que el operador ejecute ninguna otra acción

#### Scenario: Métricas reportadas para cada stack
- **WHEN** se completa el bloque de medición de `tasks.md` para un stack
- **THEN** `design.md` contiene, para ese stack, valores observados (mín, mediana, máx) de `time-to-Ready` y de `time-to-first-event` sobre al menos 3 corridas

#### Scenario: No-duplicación tras recuperación
- **WHEN** el consumidor del sink CDC recibe eventos antes y después de la eliminación del pod
- **THEN** ningún evento cuyo offset fuera ≤ al último confirmado antes del delete aparece reemitido tras la recuperación
