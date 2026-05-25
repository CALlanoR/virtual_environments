## ADDED Requirements

### Requirement: Estructura `mini-kubernetes/` con dos stacks paralelos

El sistema SHALL crear un directorio `withReplica/mini-kubernetes/` con subdirectorios autocontenidos `mysql5.7/` y `mysql8/`, cada uno conteniendo los manifiestos YAML para desplegar el stack completo en su propio namespace (`cdc-mysql57` y `cdc-mysql8` respectivamente), de modo que ambos puedan desplegarse en el mismo cluster sin conflicto.

#### Scenario: Existencia de los dos subdirectorios
- **WHEN** se inspecciona `withReplica/mini-kubernetes/`
- **THEN** existen los subdirectorios `mysql5.7/` y `mysql8/`, cada uno con al menos un manifiesto YAML que define el Namespace correspondiente

#### Scenario: Namespaces disjuntos
- **WHEN** se inspeccionan los manifiestos de Namespace de ambos stacks
- **THEN** el stack 5.7 declara `metadata.name: cdc-mysql57` y el stack 8 declara `metadata.name: cdc-mysql8`

#### Scenario: Despliegue simultáneo de ambos stacks
- **WHEN** el usuario aplica los manifiestos de ambos stacks en un mismo cluster minikube
- **THEN** todos los Pods alcanzan estado `Ready` sin que los Services de un namespace colisionen con los del otro

### Requirement: MySQL primary y replica como StatefulSet por stack

El sistema SHALL desplegar, dentro de cada stack, dos StatefulSets — `mysql-primary` y `mysql-replica` — usando la misma imagen que el docker-compose equivalente (`mysql:5.7` para el stack 5.7 y `mysql:8.0` para el stack 8.0). Cada StatefulSet SHALL tener un PersistentVolumeClaim para el datadir y un Service headless para nombre DNS estable.

#### Scenario: Imagen del stack 5.7
- **WHEN** se inspecciona el StatefulSet `mysql-primary` o `mysql-replica` del stack 5.7
- **THEN** la imagen declarada es `mysql:5.7`

#### Scenario: Imagen del stack 8
- **WHEN** se inspecciona el StatefulSet `mysql-primary` o `mysql-replica` del stack 8
- **THEN** la imagen declarada es `mysql:8.0`

#### Scenario: PersistentVolumeClaim por instancia
- **WHEN** se inspecciona cualquier StatefulSet MySQL del laboratorio
- **THEN** declara un `volumeClaimTemplates` con `accessModes: ["ReadWriteOnce"]` montado en `/var/lib/mysql`

### Requirement: Replicación primary→replica activa en cada stack

El sistema SHALL configurar `mysql-primary` como source y `mysql-replica` como replica usando GTID y formato `ROW`, de tal forma que tras el despliegue la réplica esté replicando activamente desde el primary, en ambos stacks.

#### Scenario: Replicación activa stack 5.7
- **WHEN** se ejecuta `SHOW SLAVE STATUS\G` contra el pod `mysql-replica-0` del namespace `cdc-mysql57` después de que ambos StatefulSets estén Ready
- **THEN** los campos `Slave_IO_Running` y `Slave_SQL_Running` reportan `Yes` y `Last_Error` está vacío

#### Scenario: Replicación activa stack 8
- **WHEN** se ejecuta `SHOW REPLICA STATUS\G` contra el pod `mysql-replica-0` del namespace `cdc-mysql8` después de que ambos StatefulSets estén Ready
- **THEN** los campos `Replica_IO_Running` y `Replica_SQL_Running` reportan `Yes` y `Last_Error` está vacío

### Requirement: Réplica reescribe cambios en su propio binlog

El sistema SHALL configurar la réplica de cada stack con `binlog_format=ROW`, `binlog_row_image=FULL` y la variable de re-logging adecuada a la versión (`log_slave_updates=ON` en 5.7, `log_replica_updates=ON` en 8.0), de modo que los cambios replicados sean consumibles por Debezium desde la réplica.

#### Scenario: log_slave_updates activo en stack 5.7
- **WHEN** se consulta `SHOW VARIABLES LIKE 'log_slave_updates'` contra `mysql-replica` del namespace `cdc-mysql57`
- **THEN** el valor reportado es `ON`

#### Scenario: log_replica_updates activo en stack 8
- **WHEN** se consulta `SHOW VARIABLES LIKE 'log_replica_updates'` contra `mysql-replica` del namespace `cdc-mysql8`
- **THEN** el valor reportado es `ON`

### Requirement: InitContainer wait-for-primary en la réplica

El sistema SHALL incluir en el StatefulSet de la réplica de cada stack un `initContainer` que bloquea el arranque hasta que el Service `mysql-primary` responda a `mysqladmin ping`, de modo que el script de bootstrap de la réplica (`CHANGE MASTER TO`/`CHANGE REPLICATION SOURCE TO`) no se ejecute antes de que el primary haya completado sus propios scripts de init.

#### Scenario: InitContainer declarado
- **WHEN** se inspecciona el StatefulSet `mysql-replica` de cualquiera de los dos stacks
- **THEN** existe un `initContainer` cuyo comando hace polling de `mysqladmin ping -h mysql-primary -uroot -p<password>` hasta éxito

#### Scenario: La replica no arranca antes del primary
- **WHEN** se aplican todos los manifiestos del stack al cluster simultáneamente
- **THEN** el container principal de `mysql-replica-0` no entra a estado `Running` hasta que el `mysql-primary-0` esté `Ready`

### Requirement: Debezium Server conectado a la réplica

El sistema SHALL desplegar en cada stack un Deployment `debezium-server` cuya configuración (`application.properties`) tenga `debezium.source.database.hostname=mysql-replica` y use un usuario `debezium` distinto de `root`. La imagen del stack 5.7 SHALL ser `debezium/server:2.4.2.Final`; la del stack 8 SHALL ser `withreplica/debezium-server-mysql:3.5.0.Final` (imagen custom local que añade el conector MySQL a `quay.io/debezium/server:3.5.0.Final`).

#### Scenario: Hostname apunta a la replica
- **WHEN** se inspecciona el ConfigMap `debezium-config` de cualquiera de los dos stacks
- **THEN** la propiedad `debezium.source.database.hostname` es `mysql-replica` y `debezium.source.database.user` es `debezium`

#### Scenario: Imagen stack 5.7
- **WHEN** se inspecciona el Deployment `debezium-server` del namespace `cdc-mysql57`
- **THEN** la imagen declarada es `debezium/server:2.4.2.Final`

#### Scenario: Imagen stack 8
- **WHEN** se inspecciona el Deployment `debezium-server` del namespace `cdc-mysql8`
- **THEN** la imagen declarada es `withreplica/debezium-server-mysql:3.5.0.Final` con `imagePullPolicy: IfNotPresent`

#### Scenario: Snapshot inicial completa
- **WHEN** Debezium arranca contra una réplica recién inicializada en cualquiera de los stacks
- **THEN** los logs del Pod `debezium-server` muestran snapshot completado y transición a streaming de binlog

### Requirement: Persistencia de offsets de Debezium

El sistema SHALL montar un PersistentVolumeClaim en `/debezium/data` del Pod `debezium-server` de cada stack, de modo que los archivos `offsets.dat` y `schema-history.dat` sobrevivan a reinicios del Pod.

#### Scenario: PVC montado
- **WHEN** se inspecciona el Deployment `debezium-server` de cualquiera de los dos stacks
- **THEN** existe un volume backed por PVC montado en `/debezium/data`

#### Scenario: Offsets persisten tras reinicio del pod
- **WHEN** se elimina el Pod `debezium-server` y k8s lo recrea
- **THEN** el archivo `/debezium/data/offsets.dat` existe con el contenido previo y Debezium retoma el streaming desde el último offset sin re-snapshotting

### Requirement: Filtrado por lista explícita de tablas

El sistema SHALL configurar Debezium Server con `debezium.source.table.include.list=inventory.customers` en ambos stacks, de modo que cambios en `inventory.audit_log` no generen eventos CDC.

#### Scenario: Cambio en customers produce evento
- **WHEN** se inserta una fila en `inventory.customers` del primary de cualquiera de los stacks
- **THEN** los logs del Pod `cdc-sink` del mismo namespace muestran un POST con un evento CDC para esa fila

#### Scenario: Cambio en audit_log es ignorado
- **WHEN** se inserta una fila en `inventory.audit_log` del primary de cualquiera de los stacks
- **THEN** los logs del Pod `cdc-sink` del mismo namespace NO muestran ningún evento CDC para esa fila

### Requirement: Sink HTTP observable vía kubectl logs

El sistema SHALL desplegar en cada stack un Deployment `cdc-sink` con imagen `mendhak/http-https-echo:40` expuesto vía un Service ClusterIP `cdc-sink:8080` interno al namespace. Debezium Server SHALL estar configurado con `debezium.sink.type=http` y `debezium.sink.http.url=http://cdc-sink:8080`.

#### Scenario: Servicio cdc-sink existe en cada namespace
- **WHEN** se ejecuta `kubectl get svc cdc-sink -n cdc-mysql57` o `... -n cdc-mysql8`
- **THEN** existe un Service de tipo ClusterIP con puerto 8080

#### Scenario: INSERT genera evento observable
- **WHEN** el usuario inserta una fila en `inventory.customers` del primary de un stack
- **THEN** `kubectl logs deploy/cdc-sink -n <namespace>` muestra un POST con un evento `op=c`

#### Scenario: UPDATE genera evento observable
- **WHEN** el usuario actualiza una fila existente en el primary
- **THEN** `kubectl logs deploy/cdc-sink -n <namespace>` muestra un POST con un evento `op=u` con `before` y `after`

#### Scenario: DELETE genera evento observable
- **WHEN** el usuario elimina una fila existente en el primary
- **THEN** `kubectl logs deploy/cdc-sink -n <namespace>` muestra un POST con un evento `op=d`

### Requirement: Datos de demo pre-cargados en el primary

El sistema SHALL crear automáticamente, durante el bootstrap del primary de cada stack, la base de datos `inventory` con las tablas `customers` (incluida en el filtro CDC) y `audit_log` (no incluida) con filas seed, montando los scripts `01-users.sql` y `02-demo-schema.sql` desde un ConfigMap en `/docker-entrypoint-initdb.d/`.

#### Scenario: Esquema demo disponible tras el arranque
- **WHEN** el StatefulSet `mysql-primary` alcanza estado `Ready` en cualquiera de los stacks
- **THEN** existe la base de datos `inventory` con las tablas `customers` y `audit_log` y filas seed

#### Scenario: Esquema demo replicado a la replica
- **WHEN** se consulta la base de datos `inventory` contra `mysql-replica` después de que ambos StatefulSets estén Ready
- **THEN** las tablas y filas son visibles, replicadas desde el primary

### Requirement: Exposición de primary y replica vía NodePort en puertos altos disjuntos

El sistema SHALL exponer cada Service de MySQL al host vía NodePort, con asignaciones que no choquen con los puertos del docker-compose existente: stack 5.7 NodePort `30306` (primary) y `30307` (replica); stack 8 NodePort `30308` (primary) y `30309` (replica).

#### Scenario: NodePort declarados
- **WHEN** se inspeccionan los Services NodePort de los cuatro MySQL del laboratorio
- **THEN** los `nodePort` asignados son exactamente 30306, 30307, 30308 y 30309 para 5.7-primary, 5.7-replica, 8-primary y 8-replica respectivamente

#### Scenario: Acceso desde el host
- **WHEN** el usuario corre `minikube service mysql-primary -n cdc-mysql8 --url` o un `kubectl port-forward` equivalente
- **THEN** puede conectarse desde el host con un cliente `mysql` y ejecutar SQL contra `inventory`

### Requirement: Load-generator como Job on-demand

El sistema SHALL incluir en `mini-kubernetes/load-generator/` un manifiesto `Job` por stack (`job-mysql5.7.yaml` y `job-mysql8.yaml`) y un ConfigMap `load-generator-script` que monta `random_changes.py` y `requirements.txt`. Cada Job SHALL usar la imagen `python:3.12-slim`, instalar PyMySQL en un initContainer y ejecutar el generador con `--host mysql-primary --port 3306 --target <stack>` apuntando al Service ClusterIP del namespace correspondiente. El Job SHALL tener `metadata.generateName` para permitir múltiples invocaciones, y `ttlSecondsAfterFinished: 300` para auto-limpieza.

#### Scenario: Job para stack 5.7
- **WHEN** se aplica `job-mysql5.7.yaml` con el stack 5.7 corriendo
- **THEN** se crea un Pod cuyo container `load-generator` ejecuta `random_changes.py --target mysql5.7 --host mysql-primary --port 3306` dentro del namespace `cdc-mysql57`

#### Scenario: Job para stack 8
- **WHEN** se aplica `job-mysql8.yaml` con el stack 8 corriendo
- **THEN** se crea un Pod cuyo container `load-generator` ejecuta `random_changes.py --target mysql8 --host mysql-primary --port 3306` dentro del namespace `cdc-mysql8`

#### Scenario: Operaciones del Job disparan eventos CDC
- **WHEN** el Pod del load-generator está ejecutando operaciones aleatorias contra el primary
- **THEN** los logs de `cdc-sink` del mismo namespace muestran eventos `op=c`, `op=u` o `op=d` correspondientes

#### Scenario: Auto-stop por duración
- **WHEN** el Job se ejecuta con los defaults (duration=40s)
- **THEN** el Pod termina con exit 0 tras ~40 segundos sin necesidad de borrado manual

#### Scenario: Auto-limpieza tras 5 minutos
- **WHEN** han pasado 300 segundos desde la finalización del Job
- **THEN** el Job y su Pod son eliminados automáticamente por el TTL controller

#### Scenario: Múltiples invocaciones coexisten
- **WHEN** se aplica `job-mysql8.yaml` dos veces seguidas mientras el primero aún corre
- **THEN** se crean dos Jobs con nombres distintos (gracias a `generateName`) y ambos corren contra el mismo primary

### Requirement: Imagen custom de Debezium 3.5 con conector MySQL

El sistema SHALL reutilizar el `Dockerfile` existente en `docker-compose/mysql8/debezium/` para construir la imagen `withreplica/debezium-server-mysql:3.5.0.Final` (basada en `quay.io/debezium/server:3.5.0.Final` + conector MySQL). El Makefile de `mini-kubernetes/` SHALL incluir targets `image-build` y `image-load` que construyen la imagen localmente y la cargan al daemon de minikube.

#### Scenario: Reuso del Dockerfile
- **WHEN** se inspecciona el target `image-build` del Makefile
- **THEN** invoca `docker build` apuntando al contexto `../docker-compose/mysql8/debezium/` (no duplica el Dockerfile)

#### Scenario: image-load contra minikube
- **WHEN** se ejecuta `make image-load`
- **THEN** la imagen `withreplica/debezium-server-mysql:3.5.0.Final` aparece en `minikube image ls`

### Requirement: Makefile top-level para mini-kubernetes

El sistema SHALL incluir un `Makefile` en `withReplica/mini-kubernetes/` con los siguientes targets, todos invocables desde ese directorio:

- `help` — listado de targets.
- `image-build` — `docker build` de la imagen custom de Debezium 3.5.
- `image-load` — `minikube image load` de la imagen custom.
- `up` — aplica los manifiestos de ambos stacks.
- `up-5.7` — aplica solo el stack 5.7.
- `up-8` — aplica solo el stack 8 (depende de `image-load`).
- `wait-healthy` — bloquea hasta que los Pods MySQL de ambos namespaces estén `Ready`.
- `ps` — `kubectl get all` en ambos namespaces.
- `logs-sink-5.7` / `logs-sink-8` — `kubectl logs -f deploy/cdc-sink` en el namespace correspondiente.
- `load-5.7` / `load-8` — aplica el Job del load-generator correspondiente.
- `down` — elimina ambos namespaces (`--ignore-not-found`).

El Makefile NO SHALL incluir targets relacionados con monitoreo.

#### Scenario: make up levanta ambos stacks
- **WHEN** se ejecuta `make up` desde `withReplica/mini-kubernetes/`
- **THEN** se aplican los manifiestos de `mysql5.7/` y `mysql8/`, creando ambos namespaces y todos sus recursos

#### Scenario: make down borra ambos namespaces
- **WHEN** se ejecuta `make down` desde `withReplica/mini-kubernetes/`
- **THEN** los namespaces `cdc-mysql57` y `cdc-mysql8` son eliminados junto con todos sus recursos y PVCs, y el comando es idempotente (no falla si no existen)

#### Scenario: make wait-healthy bloquea hasta Ready
- **WHEN** se ejecuta `make wait-healthy` después de un `make up` reciente
- **THEN** el comando bloquea hasta que los cuatro Pods MySQL (dos por stack) estén `Ready` y termina con exit 0

#### Scenario: make load-8 dispara un Job
- **WHEN** se ejecuta `make load-8` con el stack 8 corriendo y Ready
- **THEN** se crea un Pod del load-generator en `cdc-mysql8` que comienza a emitir operaciones contra `mysql-primary`

#### Scenario: make help no menciona monitoreo
- **WHEN** se ejecuta `make help`
- **THEN** la lista de targets NO incluye ningún target relacionado con `monitoring/` ni con `run-comparison.sh`

### Requirement: Documentación de uso en README

El sistema SHALL incluir un `README.md` en `withReplica/mini-kubernetes/` que documente:

- Prerrequisitos (minikube, kubectl, GNU make, recursos mínimos sugeridos).
- Topología (diagrama equivalente al del docker-compose, adaptado a k8s).
- Diferencias con docker-compose (NodePorts en lugar de host ports, namespaces, ConfigMaps).
- Pasos de bootstrap (`image-build`, `image-load`, `up`, `wait-healthy`).
- Cómo observar eventos (`make logs-sink-8`, `kubectl logs`).
- Cómo generar carga (`make load-8`).
- Cómo conectarse al primary desde el host (NodePort + `minikube service` o `kubectl port-forward`).
- Limpieza (`make down`).
- Troubleshooting (los mismos casos comunes que el README del docker-compose: replica no arranca, Debezium no se conecta, etc., adaptados a k8s).

#### Scenario: README incluye comandos esenciales
- **WHEN** un nuevo usuario abre `withReplica/mini-kubernetes/README.md`
- **THEN** encuentra al menos: comando para construir y cargar la imagen custom, comando para levantar (`make up`), comando para conectarse al primary, comando para seguir logs del cdc-sink, comando para correr el generador, y comando para tear-down

#### Scenario: README documenta los NodePorts
- **WHEN** se lee la sección de acceso al cluster
- **THEN** se documenta explícitamente que los puertos NodePort son 30306-30309 para no chocar con el docker-compose

### Requirement: No portar el monitoreo

El sistema NO SHALL incluir manifiestos, Jobs, CronJobs ni documentación relacionada con `docker-compose/monitoring/` (scripts `monitor-mysql5.7.sh`, `monitor-mysql8.sh`, `run-comparison.sh`, ni el código de `plot/`).

#### Scenario: No hay manifiestos de monitoreo
- **WHEN** se busca recursivamente en `withReplica/mini-kubernetes/` cualquier referencia a `monitoring`, `monitor-mysql`, `run-comparison` o `plot`
- **THEN** no se encuentra ninguna coincidencia

#### Scenario: README explica omisión
- **WHEN** se lee el README de `mini-kubernetes/`
- **THEN** se menciona explícitamente que el monitoreo (presente en `docker-compose/monitoring/`) queda fuera del alcance de esta variante y puede añadirse en un cambio futuro
