## 0. Inventario de archivos YAML

Esta sección es referencia, no tareas accionables. Describe brevemente qué función cumple cada archivo YAML que este change **crea** o **modifica**, para que cualquiera que retome el change entienda el rol de cada pieza antes de tocarla.

### Archivos nuevos

#### `minikube/mysql5.7/04a-mysql-debezium-state.yaml` y `minikube/mysql8/04a-mysql-debezium-state.yaml`

Manifest único por stack que despliega toda la infraestructura del state-store dedicado. Cada archivo contiene cinco recursos en orden:

1. **`PersistentVolumeClaim debezium-state-data`** — almacenamiento persistente para el datadir del MySQL del state-store (`/var/lib/mysql` dentro del contenedor). `ReadWriteOnce`, ~500Mi. Sobrevive a recreaciones del Pod; **no** se elimina cuando se borra el Pod.
2. **`ConfigMap mysql-debezium-state-initdb`** — script SQL que MySQL ejecuta la **primera** vez que arranca con un datadir vacío. Crea la DB `dbz_state`, las tablas `offset_storage` y `schema_history` con el esquema esperado por `debezium-storage-jdbc`, y el usuario `dbz_state@'%'` con privilegios CRUD acotados.
3. **`Service mysql-debezium-state`** — endpoint estable DNS-resoluble (`mysql-debezium-state.<ns>.svc.cluster.local`) que abstrae al Pod del MySQL. Es el hostname que Debezium pone en su `jdbc.url`. `ClusterIP`, port 3306.
4. **`Deployment mysql-debezium-state`** — un Pod corriendo `mysql:5.7` (en el stack 5.7) o `mysql:8.0` (en el stack 8), montando el PVC y el initdb. 1 réplica.
5. **`Secret debezium-state-credentials`** — passwords del usuario `dbz_state` y de root. Lo consumen tanto el initdb (para crear el usuario y setear root password) como el Deployment de Debezium (vía env var).

#### `minikube/images/debezium-server-mysql57-jdbc/Dockerfile` *(no es YAML, pero es infraestructura)*

Dockerfile que extiende `debezium/server:2.4.2.Final` y agrega `debezium-storage-jdbc-2.4.2.Final.jar` (bajado de Maven Central) a `/debezium/lib/`. Produce la imagen `withreplica/debezium-server-mysql57-jdbc:2.4.2.Final` que el stack mysql5.7 necesita para usar `JdbcOffsetBackingStore` / `JdbcSchemaHistory`. Se cita aquí por ser parte de la infraestructura de este change aunque no sea YAML.

### Archivos modificados

#### `minikube/mysql5.7/01-configmaps.yaml` y `minikube/mysql8/01-configmaps.yaml`

Estos ConfigMaps existen y contienen varias entradas para todo el stack (config de MySQL primary, MySQL replica, initdb de cada uno, healthcheck del replica, **y `debezium-config`**). Este change **sólo** toca el ConfigMap `debezium-config`, que es el `application.properties` que Debezium server lee al arrancar. Específicamente: cambia `debezium.source.offset.storage` y `debezium.source.schema.history.internal` de `File*` a `Jdbc*`, agrega `jdbc.url / jdbc.user / jdbc.password / jdbc.*.table.name` para ambos stores, y borra las propiedades `*.file.filename` que quedan obsoletas. El resto del archivo (configs de MySQL primary/replica/healthcheck) **no se toca**.

#### `minikube/mysql5.7/02-secrets.yaml` y `minikube/mysql8/02-secrets.yaml`

Estos manifests contienen los Secrets con las credenciales de los MySQL del stack (root password, replication user, debezium user). Este change **agrega** un Secret nuevo `debezium-state-credentials` con dos keys: `dbz-state-password` (password del usuario `dbz_state` que escribe offset/history) y `root-password` (password de root del MySQL del state-store, usado solo en arranque inicial vía `MYSQL_ROOT_PASSWORD` env). Los Secrets pre-existentes (`mysql-credentials`, etc.) **no se modifican**.

#### `minikube/mysql5.7/06-debezium-server.yaml` y `minikube/mysql8/06-debezium-server.yaml`

Manifest del Deployment de `debezium-server` + el PVC `debezium-data` que se usa hoy para guardar offset/history en file. Este change:

- **Elimina** el `PersistentVolumeClaim debezium-data` (queda obsoleto, no hay más archivos que persistir localmente).
- **Elimina** el `volume` con name `data` y su `volumeMount` en `/debezium/data`.
- **Agrega** un bloque `env:` con `DBZ_STATE_PASSWORD` valueFrom `secretKeyRef` apuntando al nuevo Secret. Debezium lo lee vía la substitución `${env:DBZ_STATE_PASSWORD}` que ya está en el ConfigMap.
- **Cambia** la `image` solo en el stack mysql5.7 (a la nueva imagen custom con el JAR de JDBC storage). El stack mysql8 mantiene su imagen actual.
- **Conserva** sin cambio: `replicas`, `strategy`, probes, resources, ConfigMap mount, selectors, labels.

### Archivos no-YAML que también se tocan

- **`minikube/Makefile`**: se agregan los targets `image-build-57 / image-load-57 / image-unload-57 / image-clean-57` siguiendo el patrón existente para la imagen de mysql8. Necesario para que `up-57` cargue automáticamente la imagen custom al cluster de minikube.

### Archivos que **no** se tocan (pero conviene conocer)

Estos archivos existen en cada stack y son parte de la infraestructura general; este change **no** los modifica, pero el state-store los acompaña en el mismo namespace:

- `00-namespace.yaml` — declara el namespace `cdc-mysql57` / `cdc-mysql8`.
- `03-mysql-primary.yaml` — StatefulSet del MySQL primary (fuente de cambios, escribe al binlog que Debezium consume).
- `04-mysql-replica.yaml` — StatefulSet del MySQL replica (read-only, lo que Debezium realmente consume — no el primary).
- `05-cdc-sink.yaml` — Deployment del receptor HTTP de los eventos CDC (donde llegan los POSTs que medimos en el experimento de RTO).

## 1. Investigación previa (bloqueante)

- [x] 1.1 Verificar el esquema exacto de las tablas que esperan `debezium-storage-jdbc-2.4.2.Final` y `debezium-storage-jdbc-3.5.0.Final` (clases `JdbcOffsetBackingStore` y `JdbcSchemaHistory`). Si los esquemas difieren entre versiones, mantener dos `initdb` distintos por stack. Si son idénticos, uno único. Documentar la conclusión en `design.md` (resolver Open Question 1).
- [x] 1.2 Confirmar que `debezium-storage-jdbc-2.4.2.Final.jar` está disponible en `https://repo1.maven.org/maven2/io/debezium/debezium-storage-jdbc/2.4.2.Final/`. Probar `curl -fsI` para asegurar HTTP 200.

## 2. Imagen custom para mysql5.7

- [x] 2.1 Crear `minikube/images/debezium-server-mysql57-jdbc/Dockerfile` siguiendo el patrón de `docker-compose/mysql8/debezium/Dockerfile`: stage `alpine` para descargar el JAR de Maven, stage final que extiende `debezium/server:2.4.2.Final` y copia el JAR a `/debezium/lib/`. Tag esperado: `withreplica/debezium-server-mysql57-jdbc:2.4.2.Final`.
- [x] 2.2 Extender `minikube/Makefile`:
  - Agregar variables `IMG_57 := withreplica/debezium-server-mysql57-jdbc:2.4.2.Final` y `DEBEZIUM_57_BUILD_CTX := ../minikube/images/debezium-server-mysql57-jdbc` (o la ruta correcta relativa al Makefile).
  - Agregar targets `image-build-57`, `image-load-57`, `image-unload-57`, `image-clean-57` siguiendo el patrón existente.
  - Actualizar `up-57` para depender de `image-load-57` (igual que `up-8` depende de `image-load`).
- [x] 2.3 `make image-build-57 && make image-load-57` y verificar con `minikube image ls | grep debezium-server-mysql57-jdbc` que la imagen está cargada.
- [x] 2.4 `docker run --rm withreplica/debezium-server-mysql57-jdbc:2.4.2.Final ls /debezium/lib/ | grep storage-jdbc` debe mostrar `debezium-storage-jdbc-2.4.2.Final.jar`.

## 3. Manifest del state-store por stack

- [x] 3.1 Crear `minikube/mysql5.7/04a-mysql-debezium-state.yaml` con:
  - `PersistentVolumeClaim debezium-state-data` (`ReadWriteOnce`, 500Mi).
  - `ConfigMap mysql-debezium-state-initdb` con `00-schema.sql` que cree DB `dbz_state`, las tablas `offset_storage` y `schema_history` (esquema según Task 1.1), y el usuario `dbz_state@'%'` con `GRANT SELECT, INSERT, UPDATE, DELETE ON dbz_state.* TO 'dbz_state'@'%'`.
  - `Secret debezium-state-credentials` (o agregarlo a `02-secrets.yaml` — ver Task 4.1) con `password` para `dbz_state` y `root-password` para root.
  - `Service mysql-debezium-state` (ClusterIP, port 3306).
  - `Deployment mysql-debezium-state` con imagen `mysql:5.7` (alineado con el stack), 1 réplica, mount del initdb en `/docker-entrypoint-initdb.d/`, mount del PVC en `/var/lib/mysql`, env vars de root password y `MYSQL_DATABASE=dbz_state`.
- [x] 3.2 Crear `minikube/mysql8/04a-mysql-debezium-state.yaml` análogo, con `mysql:8.0` como imagen.
- [x] 3.3 Validar que ambos manifests pasan `kubectl --dry-run=client apply -f` antes de aplicarlos.

## 4. Secrets

- [x] 4.1 Modificar `minikube/mysql5.7/02-secrets.yaml` y `minikube/mysql8/02-secrets.yaml` para incluir `debezium-state-credentials` con dos keys: `dbz-state-password` y `root-password`. Generar passwords aleatorios largos (no reusar los valores demo). Documentar el método (p.ej. `openssl rand -base64 32`) en `runbook.md`.

## 5. Config de Debezium en ambos stacks

- [x] 5.1 Modificar `minikube/mysql5.7/01-configmaps.yaml` (ConfigMap `debezium-config`, archivo `application.properties`):
  - Reemplazar:
    ```
    debezium.source.offset.storage=org.apache.kafka.connect.storage.FileOffsetBackingStore
    debezium.source.offset.storage.file.filename=/debezium/data/offsets.dat
    ```
    por:
    ```
    debezium.source.offset.storage=io.debezium.storage.jdbc.offset.JdbcOffsetBackingStore
    debezium.source.offset.storage.jdbc.url=jdbc:mysql://mysql-debezium-state:3306/dbz_state?useSSL=false
    debezium.source.offset.storage.jdbc.user=dbz_state
    debezium.source.offset.storage.jdbc.password=${env:DBZ_STATE_PASSWORD}
    debezium.source.offset.storage.jdbc.offset.table.name=offset_storage
    ```
  - Reemplazar:
    ```
    debezium.source.schema.history.internal=io.debezium.storage.file.history.FileSchemaHistory
    debezium.source.schema.history.internal.file.filename=/debezium/data/schema-history.dat
    ```
    por:
    ```
    debezium.source.schema.history.internal=io.debezium.storage.jdbc.history.JdbcSchemaHistory
    debezium.source.schema.history.internal.jdbc.url=jdbc:mysql://mysql-debezium-state:3306/dbz_state?useSSL=false
    debezium.source.schema.history.internal.jdbc.user=dbz_state
    debezium.source.schema.history.internal.jdbc.password=${env:DBZ_STATE_PASSWORD}
    debezium.source.schema.history.internal.jdbc.history.table.name=schema_history
    ```
- [x] 5.2 Aplicar los mismos cambios en `minikube/mysql8/01-configmaps.yaml`.
- [x] 5.3 Confirmar que `database.include.list` sigue siendo `inventory` (no agregar `dbz_state`).

## 6. Deployment de debezium-server

- [x] 6.1 Modificar `minikube/mysql5.7/06-debezium-server.yaml`:
  - Cambiar `image:` a `withreplica/debezium-server-mysql57-jdbc:2.4.2.Final`.
  - Eliminar el volume `data` y su `volumeMount` en `/debezium/data`.
  - Eliminar el PVC `debezium-data` del manifest (queda obsoleto).
  - Agregar `env: DBZ_STATE_PASSWORD valueFrom: secretKeyRef: name=debezium-state-credentials key=dbz-state-password`.
  - Mantener probes, replicas, strategy, resources, ConfigMap mount, sin cambios.
- [x] 6.2 Aplicar los mismos cambios en `minikube/mysql8/06-debezium-server.yaml`, manteniendo la imagen `withreplica/debezium-server-mysql:3.5.0.Final`.

## 7. Aplicación y verificación

- [x] 7.1 En `cdc-mysql57`: aplicar en orden — `02-secrets.yaml`, `04a-mysql-debezium-state.yaml`, esperar `kubectl rollout status deployment/mysql-debezium-state -n cdc-mysql57 --timeout=120s`, luego `01-configmaps.yaml`, finalmente `06-debezium-server.yaml`.
- [x] 7.2 Repetir 7.1 en `cdc-mysql8`.
- [x] 7.3 Verificar que `kubectl get pods -n cdc-mysql57` y `cdc-mysql8` muestran el `mysql-debezium-state` `Ready=1/1` y el `debezium-server` con `RESTARTS=0` tras 60s.
- [x] 7.4 `kubectl exec -n cdc-mysql57 deploy/mysql-debezium-state -- mysql -u dbz_state -p<pw> -e "SELECT COUNT(*) FROM dbz_state.offset_storage; SELECT COUNT(*) FROM dbz_state.schema_history;"` debe retornar > 0 en ambas. Repetir para mysql8.
- [x] 7.5 Borrar el PVC viejo: `kubectl delete pvc debezium-data -n cdc-mysql57` y `kubectl delete pvc debezium-data -n cdc-mysql8`. Confirmar que no hay PVC bound al Deployment de debezium.
- [x] 7.6 Generar carga con `minikube/scripts/loadgen-long.yaml` (sed + apply) y confirmar que el sink recibe eventos `op=c/u/d` y que `SELECT MAX(record_insert_ts) FROM dbz_state.offset_storage` avanza con el tiempo.

## 8. Re-medición de RTO (regresión)

- [x] 8.1 Ejecutar `minikube/scripts/rto_experiment.sh 3`.
- [x] 8.2 Comparar la mediana de `time_to_ready_seconds` y `time_to_first_event_seconds` contra la baseline (22.16s / 6.11s en mysql57, 22.24s / 5.52s en mysql8). Esperado: sin degradación significativa (±10%). Si hay regresión, documentar y reabrir Decisión 1 antes de archivar.
- [x] 8.3 Verificar no-duplicación: el consumidor del sink no recibe eventos cuyo offset previo al delete sea reemitido (mismo Requirement heredado).

## 9. Documentación

- [x] 9.1 Crear `openspec/changes/migrate-debezium-state-to-mysql/runbook.md` con la bitácora paso a paso del experimento, los comandos `kubectl` ejecutados, el output relevante, los valores del re-experimento RTO y un anexo de troubleshooting (qué hacer si Debezium falla al conectar al state-store, qué pasa si se borra una tabla del state-store por error, cómo regenerar passwords).
- [x] 9.2 Documentar en `runbook.md` el procedimiento de **rollback**: re-aplicar `06-debezium-server.yaml` y `01-configmaps.yaml` de la versión pre-migration, recrear el PVC `debezium-data`, re-snapshotear `inventory.customers`. Aceptable que el rollback implique re-snapshot.

## 10. Cierre

- [x] 10.1 `openspec validate migrate-debezium-state-to-mysql --type change --strict` y corregir errores de formato.
- [x] 10.2 Marcar listo para archivar.
