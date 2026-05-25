## MODIFIED Requirements

### Requirement: Configuración actual bajo evaluación

El Deployment `debezium-server` se despliega en el namespace único `cdc-lab` (no en namespaces per-stack como antes). Existen dos Deployments coexistiendo en el mismo namespace, distinguidos por sufijo en el nombre y por label: `debezium-server-57` (con label `stack: mysql57`) y `debezium-server-8` (con label `stack: mysql8`). Ambos SHALL declarar `spec.replicas: 1` y `spec.strategy.type: Recreate`.

#### Scenario: replicas=1 y strategy Recreate en `debezium-server-57`
- **WHEN** se inspecciona el Deployment `debezium-server-57` en el namespace `cdc-lab`
- **THEN** declara `spec.replicas: 1`, `spec.strategy.type: Recreate` y `metadata.labels.stack: mysql57`

#### Scenario: replicas=1 y strategy Recreate en `debezium-server-8`
- **WHEN** se inspecciona el Deployment `debezium-server-8` en el namespace `cdc-lab`
- **THEN** declara `spec.replicas: 1`, `spec.strategy.type: Recreate` y `metadata.labels.stack: mysql8`

#### Scenario: Selector por label aísla un stack
- **WHEN** se ejecuta `kubectl get pods -n cdc-lab -l stack=mysql57`
- **THEN** la salida contiene exactamente los pods del stack 5.7 (`mysql-primary-57`, `mysql-replica-57`, `cdc-sink-57`, `debezium-server-57-...`) y ninguno del stack 8

### Requirement: Probes mínimas presentes en ambos manifests

El Deployment `debezium-server-57` y `debezium-server-8` SHALL declarar `livenessProbe` HTTP a `/q/health/live:8080` y `readinessProbe` HTTP a `/q/health/ready:8080`, con los valores ya validados en `evaluate-debezium-server-ha`.

#### Scenario: livenessProbe y readinessProbe en `debezium-server-57`
- **WHEN** se inspecciona el contenedor principal de `debezium-server-57`
- **THEN** declara `livenessProbe.httpGet.path: /q/health/live` y `readinessProbe.httpGet.path: /q/health/ready`, ambos en port `8080`

#### Scenario: livenessProbe y readinessProbe en `debezium-server-8`
- **WHEN** se inspecciona el contenedor principal de `debezium-server-8`
- **THEN** declara `livenessProbe.httpGet.path: /q/health/live` y `readinessProbe.httpGet.path: /q/health/ready`, ambos en port `8080`

### Requirement: Durabilidad del offset y schema history

`debezium-server-57` y `debezium-server-8` SHALL persistir su offset del binlog y schema history en un **único** `mysql-debezium-state` compartido (Deployment + Service en `cdc-lab`), usando `JdbcOffsetBackingStore` y `JdbcSchemaHistory`. Cada Debezium SHALL apuntar a una **base de datos lógica distinta** del state-store (`dbz_state_57` o `dbz_state_8`) y SHALL autenticar con un **usuario distinto** (`dbz_state_57` o `dbz_state_8`) sin grants cruzados entre DBs.

#### Scenario: JDBC URL apunta a la DB correcta por stack
- **WHEN** se inspeccionan los ConfigMaps `debezium-config-57` y `debezium-config-8`
- **THEN** `debezium-config-57` declara `debezium.source.offset.storage.jdbc.url=jdbc:mysql://mysql-debezium-state:3306/dbz_state_57` y `debezium-config-8` declara la URL análoga con `dbz_state_8`

#### Scenario: Usuarios JDBC distintos por stack
- **WHEN** se inspeccionan los ConfigMaps `debezium-config-57` y `debezium-config-8`
- **THEN** `debezium-config-57` declara `debezium.source.offset.storage.jdbc.user=dbz_state_57` y `debezium-config-8` declara `dbz_state_8`

#### Scenario: No-duplicación tras recuperación
- **WHEN** se elimina el pod activo de `debezium-server-57` con `kubectl delete pod ... --grace-period=0 --force` y un pod sustituto arranca
- **THEN** el consumidor del `cdc-sink-57` no recibe eventos cuyo offset confirmado en `dbz_state_57.offset_storage` antes del delete sea reemitido

## ADDED Requirements

### Requirement: Namespace único `cdc-lab`

Todo el lab (mysql primaries, mysql replicas, cdc-sinks, debezium-servers y el state-store) SHALL vivir en un único namespace `cdc-lab`. Los namespaces `cdc-mysql57` y `cdc-mysql8` SHALL no existir tras el cierre de este change.

#### Scenario: Namespace `cdc-lab` existe
- **WHEN** se ejecuta `kubectl get namespace cdc-lab`
- **THEN** el namespace existe y está `Active`

#### Scenario: Namespaces viejos eliminados
- **WHEN** se ejecuta `kubectl get namespace cdc-mysql57 cdc-mysql8`
- **THEN** ambos retornan `NotFound`

### Requirement: State-store único compartido con DBs lógicas aisladas

Existe un único Deployment `mysql-debezium-state` en `cdc-lab` con dos DBs lógicas (`dbz_state_57` y `dbz_state_8`) y dos usuarios MySQL (`dbz_state_57`, `dbz_state_8`) sin grants cruzados entre DBs. Cada DB SHALL contener las tablas `offset_storage` y `schema_history` con el esquema esperado por `debezium-storage-jdbc` (PRIMARY KEY explícito, `history_data` tipo `MEDIUMTEXT`).

#### Scenario: Una sola DB para state-store, dos DBs lógicas adentro
- **WHEN** se ejecuta `SHOW DATABASES` en el Pod `mysql-debezium-state`
- **THEN** la salida incluye `dbz_state_57` y `dbz_state_8` (entre otras DBs del sistema)

#### Scenario: Usuarios distintos por stack
- **WHEN** se ejecuta `SELECT user, plugin FROM mysql.user WHERE user LIKE 'dbz_state%'`
- **THEN** la salida lista exactamente dos filas: `dbz_state_57` y `dbz_state_8`, ambos con plugin `mysql_native_password`

#### Scenario: Aislamiento de privilegios entre stacks
- **WHEN** un usuario `dbz_state_57` intenta `SELECT * FROM dbz_state_8.offset_storage`
- **THEN** MySQL retorna error `1142 (42000): ... command denied to user 'dbz_state_57'@'...' for table 'offset_storage'`

#### Scenario: Single Pod del state-store
- **WHEN** se ejecuta `kubectl get pods -n cdc-lab -l app=mysql-debezium-state`
- **THEN** la salida lista exactamente un pod (no dos)

### Requirement: Nombres con sufijo y labels `stack` en recursos per-stack

Todos los recursos que existían duplicados por-stack pre-consolidación SHALL llevar sufijo `-57` o `-8` en su `metadata.name`, y la label `stack: mysql57` o `stack: mysql8` en sus `metadata.labels`. Esto aplica a: StatefulSets, Deployments, Services, ConfigMaps, Secrets, Jobs y Pods. Los recursos compartidos (`mysql-debezium-state`, `debezium-state-credentials`, namespace) **no** llevan sufijo.

#### Scenario: Recursos del stack 5.7 con sufijo `-57`
- **WHEN** se ejecuta `kubectl get all,cm,secrets -n cdc-lab -l stack=mysql57 -o name`
- **THEN** todos los recursos listados tienen `-57` como sufijo en su nombre

#### Scenario: Recursos del stack 8 con sufijo `-8`
- **WHEN** se ejecuta `kubectl get all,cm,secrets -n cdc-lab -l stack=mysql8 -o name`
- **THEN** todos los recursos listados tienen `-8` como sufijo en su nombre

#### Scenario: Recursos compartidos sin sufijo
- **WHEN** se inspeccionan los recursos en `minikube/shared/`
- **THEN** el Deployment, Service y PVC del state-store se llaman `mysql-debezium-state` (sin sufijo); el Secret se llama `debezium-state-credentials` (sin sufijo)
