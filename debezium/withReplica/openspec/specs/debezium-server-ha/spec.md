# debezium-server-ha Specification

## Purpose

Capacidad de evaluación y contrato operacional para la alta disponibilidad del Deployment `debezium-server` en minikube (stacks `cdc-mysql57` y `cdc-mysql8`). Define la configuración bajo evaluación (`replicas: 1`, `strategy: Recreate`), la presencia de probes que hacen observable el estado funcional del pod, la persistencia de offset y schema history en una **MySQL dedicada** por stack (`mysql-debezium-state`) vía `debezium-storage-jdbc`, y el contrato de recuperación tras caída del pod activo (con métricas `time-to-Ready` y `time-to-first-event` reportadas por stack).

## Requirements

### Requirement: Configuración actual bajo evaluación

El Deployment `debezium-server` en ambos stacks (`cdc-mysql57` y `cdc-mysql8`) SHALL declarar `spec.replicas: 1` y `spec.strategy.type: Recreate`. Esta es la configuración cuyo comportamiento de recuperación se evalúa; cualquier desviación invalida los resultados de la medición.

#### Scenario: replicas=1 y strategy Recreate en stack 5.7
- **WHEN** se inspecciona `minikube/mysql5.7/06-debezium-server.yaml`
- **THEN** el Deployment `debezium-server` declara `spec.replicas: 1` y `spec.strategy.type: Recreate`

#### Scenario: replicas=1 y strategy Recreate en stack 8
- **WHEN** se inspecciona `minikube/mysql8/06-debezium-server.yaml`
- **THEN** el Deployment `debezium-server` declara `spec.replicas: 1` y `spec.strategy.type: Recreate`

### Requirement: Probes mínimas presentes en ambos manifests

El Deployment `debezium-server` SHALL declarar al menos `livenessProbe` y `readinessProbe` en ambos stacks, con valores que permitan que `Ready=True` refleje que Debezium completó el bootstrap y no solo que el contenedor arrancó.

#### Scenario: livenessProbe y readinessProbe en stack 5.7
- **WHEN** se inspecciona el contenedor principal en `minikube/mysql5.7/06-debezium-server.yaml`
- **THEN** el contenedor declara `livenessProbe` y `readinessProbe`

#### Scenario: livenessProbe y readinessProbe en stack 8
- **WHEN** se inspecciona el contenedor principal en `minikube/mysql8/06-debezium-server.yaml`
- **THEN** el contenedor declara `livenessProbe` y `readinessProbe`

### Requirement: Durabilidad del offset y schema history

El `debezium-server` SHALL persistir el offset del binlog y el historial de schemas en una base de datos MySQL dedicada y aislada del path de CDC, llamada `mysql-debezium-state`, mediante los backing stores `io.debezium.storage.jdbc.offset.JdbcOffsetBackingStore` y `io.debezium.storage.jdbc.history.JdbcSchemaHistory`. Esta DB SHALL ser independiente del primary y del replica que Debezium consume; el offset SHALL sobrevivir a `kubectl delete pod -l app=debezium-server` y SHALL permitir que el pod sustituto reanude desde el último offset confirmado sin emitir eventos duplicados al sink.

#### Scenario: Backing store JDBC para offset en stack 5.7
- **WHEN** se inspecciona el ConfigMap `debezium-config` del namespace `cdc-mysql57`
- **THEN** `debezium.source.offset.storage` vale `io.debezium.storage.jdbc.offset.JdbcOffsetBackingStore` y `debezium.source.offset.storage.jdbc.url` apunta a `jdbc:mysql://mysql-debezium-state:3306/dbz_state` (con o sin parámetros)

#### Scenario: Backing store JDBC para offset en stack 8
- **WHEN** se inspecciona el ConfigMap `debezium-config` del namespace `cdc-mysql8`
- **THEN** `debezium.source.offset.storage` vale `io.debezium.storage.jdbc.offset.JdbcOffsetBackingStore` y `debezium.source.offset.storage.jdbc.url` apunta a `jdbc:mysql://mysql-debezium-state:3306/dbz_state`

#### Scenario: Schema history JDBC en ambos stacks
- **WHEN** se inspecciona `debezium.source.schema.history.internal` en cualquiera de los dos ConfigMaps
- **THEN** vale `io.debezium.storage.jdbc.history.JdbcSchemaHistory` y `debezium.source.schema.history.internal.jdbc.url` apunta a `jdbc:mysql://mysql-debezium-state:3306/dbz_state`

#### Scenario: No-duplicación tras recuperación con backing store JDBC
- **WHEN** se elimina el pod activo de `debezium-server` con `kubectl delete pod ... --grace-period=0 --force` y un pod sustituto arranca
- **THEN** el consumidor del sink no recibe eventos cuyo offset confirmado en `dbz_state.offset_storage` antes del delete sea reemitido

#### Scenario: El PVC `debezium-data` ya no se monta
- **WHEN** se inspecciona el Deployment `debezium-server` en cualquiera de los dos manifests
- **THEN** no declara un `volumeMount` en `/debezium/data` ni un `volume` que referencie un PVC `debezium-data`

### Requirement: MySQL state-store dedicado por stack

Cada stack (`cdc-mysql57` y `cdc-mysql8`) SHALL desplegar un Deployment + Service `mysql-debezium-state` dentro de su namespace, con su propio PVC `debezium-state-data` (`ReadWriteOnce`, ≥500Mi), una base de datos lógica `dbz_state` y un usuario `dbz_state@'%'` con privilegios `SELECT, INSERT, UPDATE, DELETE, CREATE` acotados a `dbz_state.*`. La DB SHALL contener al menos las tablas `offset_storage` y `schema_history` con el esquema esperado por `debezium-storage-jdbc` de la versión correspondiente al stack.

#### Scenario: Deployment y Service presentes en stack 5.7
- **WHEN** se inspeccionan los manifests de `minikube/mysql5.7/`
- **THEN** existe un Deployment `mysql-debezium-state` con 1 réplica y un Service `mysql-debezium-state` (ClusterIP, port 3306) en el namespace `cdc-mysql57`

#### Scenario: Deployment y Service presentes en stack 8
- **WHEN** se inspeccionan los manifests de `minikube/mysql8/`
- **THEN** existe un Deployment `mysql-debezium-state` con 1 réplica y un Service `mysql-debezium-state` (ClusterIP, port 3306) en el namespace `cdc-mysql8`

#### Scenario: Usuario con privilegios acotados
- **WHEN** se inspecciona el ConfigMap initdb de cualquiera de los dos stacks
- **THEN** declara la creación del usuario `dbz_state@'%'` con `GRANT SELECT, INSERT, UPDATE, DELETE, CREATE ON dbz_state.* TO 'dbz_state'@'%'` (no se otorgan `DROP`, `ALTER`, `SUPER`, ni privilegios sobre otras bases)

#### Scenario: Tablas pre-creadas en el initdb
- **WHEN** el Pod `mysql-debezium-state` arranca por primera vez con su PVC vacío
- **THEN** el initdb crea las tablas `offset_storage` y `schema_history` en la DB `dbz_state` antes de que Debezium se conecte por primera vez

#### Scenario: Aislamiento del path CDC
- **WHEN** se inspecciona `debezium.source.database.include.list` en cualquiera de los dos ConfigMaps
- **THEN** la lista contiene `inventory` y no contiene `dbz_state`

### Requirement: Imagen Debezium incluye `debezium-storage-jdbc`

La imagen de Debezium usada por cada stack SHALL incluir el JAR `debezium-storage-jdbc-<version>.Final.jar` en su classpath (`/debezium/lib/`), de modo que las clases `JdbcOffsetBackingStore` y `JdbcSchemaHistory` resuelvan correctamente al arrancar. El stack `cdc-mysql8` SHALL usar la imagen `withreplica/debezium-server-mysql:3.5.0.Final` (que ya incluye `debezium-storage-jdbc-3.5.0.Final.jar`); el stack `cdc-mysql57` SHALL usar una imagen custom `withreplica/debezium-server-mysql57-jdbc:2.4.2.Final` que extienda la imagen oficial `debezium/server:2.4.2.Final` y agregue `debezium-storage-jdbc-2.4.2.Final.jar` (descargado de Maven Central durante el build).

#### Scenario: JAR presente en imagen de stack 8
- **WHEN** se ejecuta `docker run --rm withreplica/debezium-server-mysql:3.5.0.Final ls /debezium/lib/` o equivalente
- **THEN** la salida incluye `debezium-storage-jdbc-3.5.0.Final.jar`

#### Scenario: JAR presente en imagen custom de stack 5.7
- **WHEN** se ejecuta `docker run --rm withreplica/debezium-server-mysql57-jdbc:2.4.2.Final ls /debezium/lib/` o equivalente
- **THEN** la salida incluye `debezium-storage-jdbc-2.4.2.Final.jar`

#### Scenario: Dockerfile de la imagen custom existe y es reproducible
- **WHEN** se inspecciona `minikube/images/debezium-server-mysql57-jdbc/`
- **THEN** existe un `Dockerfile` que (a) extiende `debezium/server:2.4.2.Final`, (b) descarga `debezium-storage-jdbc-2.4.2.Final.jar` de `repo1.maven.org` durante el build y (c) lo copia a `/debezium/lib/` con permisos legibles por el usuario `jboss`

#### Scenario: Makefile soporta build y load de la imagen custom de 5.7
- **WHEN** se inspecciona `minikube/Makefile`
- **THEN** declara los targets `image-build-57`, `image-load-57`, `image-unload-57`, `image-clean-57` siguiendo el mismo patrón que los targets existentes para la imagen de mysql8

### Requirement: Credenciales del state-store en Secret + env var

El password del usuario `dbz_state` SHALL vivir en un Secret de Kubernetes (`debezium-state-credentials`) en cada namespace y SHALL inyectarse al pod `debezium-server` como variables de entorno con nombre derivado de las properties de Quarkus: `DEBEZIUM_SOURCE_OFFSET_STORAGE_JDBC_PASSWORD` y `DEBEZIUM_SOURCE_SCHEMA_HISTORY_INTERNAL_JDBC_PASSWORD`. El password SHALL no aparecer en ningún ConfigMap, manifest o archivo versionado en claro.

#### Scenario: Secret presente en ambos namespaces
- **WHEN** se inspeccionan los manifests de Secrets de cada stack
- **THEN** existe un Secret `debezium-state-credentials` con (al menos) las keys `dbz-state-password` y `root-password`

#### Scenario: Env vars inyectadas al Deployment
- **WHEN** se inspecciona el contenedor principal de `debezium-server` en cualquiera de los dos Deployments
- **THEN** declara dos `env` con `name: DEBEZIUM_SOURCE_OFFSET_STORAGE_JDBC_PASSWORD` y `name: DEBEZIUM_SOURCE_SCHEMA_HISTORY_INTERNAL_JDBC_PASSWORD`, ambos `valueFrom.secretKeyRef.name: debezium-state-credentials`, `key: dbz-state-password`

#### Scenario: No hay password en claro en los ConfigMaps
- **WHEN** se inspeccionan los ConfigMaps `debezium-config` de ambos stacks
- **THEN** los campos `*.jdbc.password` no aparecen en `application.properties` (las propiedades se override vía las env vars del Deployment)

### Requirement: Recuperación medida tras caída del pod activo

Cuando el pod activo de `debezium-server` se elimina con `kubectl delete pod ... --grace-period=0 --force`, el Deployment controller SHALL recrear un pod sustituto que reanuda el consumo del binlog sin intervención manual. La evaluación SHALL reportar, para cada stack, dos métricas separadas: `time-to-Ready` y `time-to-first-event`.

#### Scenario: El pod se recrea sin intervención
- **WHEN** se ejecuta `kubectl delete pod -l app=debezium-server -n <ns> --grace-period=0 --force` en cualquiera de los stacks
- **THEN** un nuevo pod con el mismo label aparece en estado `Ready=True` sin que el operador ejecute ninguna otra acción

#### Scenario: Métricas reportadas para cada stack
- **WHEN** se completa el bloque de medición para un stack
- **THEN** existe registro (en `design.md` o `runbook.md` del change correspondiente) con valores observados (mín, mediana, máx) de `time-to-Ready` y de `time-to-first-event` sobre al menos 3 corridas

#### Scenario: No-duplicación tras recuperación
- **WHEN** el consumidor del sink CDC recibe eventos antes y después de la eliminación del pod
- **THEN** ningún evento cuyo offset fuera ≤ al último confirmado antes del delete aparece reemitido tras la recuperación
