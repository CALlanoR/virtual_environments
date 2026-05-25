## Why

Hoy el `debezium-server` de cada stack persiste su offset del binlog (`offsets.dat`) y el historial de schemas (`schema-history.dat`) en un PVC `ReadWriteOnce` (`debezium-data`, 100Mi). Esto tiene varios problemas:

- **Ata el pod a un nodo.** `ReadWriteOnce` impide que el pod se mueva libremente si en algún momento se va a un cluster multi-nodo.
- **El estado no es consultable.** Para saber en qué offset está Debezium hay que `kubectl exec` y leer el archivo. No hay SQL ni herramientas estándar.
- **Acoplamiento al lifecycle del Pod/PVC.** Si por error se borra el PVC, se pierde el offset y hay que re-snapshotear desde cero.
- **No es la forma en que está pensado correr esto en producción.** Allá la base de datos vive fuera de Kubernetes; pero **no podemos escribir en el primary** (constraint del DBA) y el replica está `read_only`. Necesitamos un store dedicado, fuera del path de CDC.

Vamos a mover **offset y schema history** a una **MySQL nueva, pequeña y dedicada por stack** (`mysql-debezium-state`), usando los backing stores que Debezium ya provee: `JdbcOffsetBackingStore` y `JdbcSchemaHistory`.

## What Changes

### Nueva infraestructura por stack
- Agregar un Deployment + Service `mysql-debezium-state` en cada namespace (`cdc-mysql57` y `cdc-mysql8`), con su propio PVC (`debezium-state-data`, ~500Mi), su propia DB lógica `dbz_state` y un usuario `dbz_state` con privilegios mínimos (`SELECT, INSERT, UPDATE, DELETE` solo sobre `dbz_state.*`).
- La DB inicializa con dos tablas vacías (las crea Debezium automáticamente la primera vez si tiene `CREATE TABLE`, o las pre-creamos con el initdb): `offset_storage` y `schema_history`.

### Imagen custom para mysql5.7
- `debezium/server:2.4.2.Final` (la imagen oficial que usa `cdc-mysql57`) **no empaca** `debezium-storage-jdbc-2.4.2.Final.jar`. Crear `minikube/images/debezium-server-mysql57-jdbc/Dockerfile` que extienda la imagen oficial y añada ese JAR (descargado de Maven Central) a `/debezium/lib/`. Tagear como `withreplica/debezium-server-mysql57-jdbc:2.4.2.Final`.
- Extender `minikube/Makefile` con `image-build-57 / image-load-57 / image-clean-57` siguiendo el patrón existente de `image-build / image-load / image-clean`.
- El stack `cdc-mysql8` ya usa `withreplica/debezium-server-mysql:3.5.0.Final` que **sí** incluye `debezium-storage-jdbc-3.5.0.Final.jar`, no hace falta cambiar imagen.

### Cambios en config y manifests de Debezium (ambos stacks)
- En `01-configmaps.yaml` (el `debezium-config`):
  - Reemplazar `debezium.source.offset.storage=org.apache.kafka.connect.storage.FileOffsetBackingStore` por `io.debezium.storage.jdbc.offset.JdbcOffsetBackingStore`, con `jdbc.url`, `jdbc.user`, `jdbc.password` (este último vía `${env:DBZ_STATE_PASSWORD}`) y `jdbc.offset.table.name=offset_storage`.
  - Reemplazar `debezium.source.schema.history.internal=io.debezium.storage.file.history.FileSchemaHistory` por `io.debezium.storage.jdbc.history.JdbcSchemaHistory`, con `jdbc.url`, `jdbc.user`, `jdbc.password` y `jdbc.history.table.name=schema_history`.
  - Borrar las propiedades `*.file.filename`.
- En `02-secrets.yaml`: agregar `debezium-state-credentials` con `password`.
- En `06-debezium-server.yaml`:
  - Quitar el volume `data` y su mount `/debezium/data`.
  - Quitar el PVC `debezium-data` del manifest (queda obsoleto).
  - Agregar `env: DBZ_STATE_PASSWORD valueFrom: secretKeyRef: name=debezium-state-credentials`.
  - En `cdc-mysql57`: cambiar `image:` a `withreplica/debezium-server-mysql57-jdbc:2.4.2.Final`.
- Las probes, `replicas`, `strategy`, `resources` y el ConfigMap mount se mantienen exactamente igual.

### Verificación post-migración
- Aplicar manifests, esperar `Ready` en ambos stacks.
- Conectarse a `mysql-debezium-state` con `mysql -u dbz_state -p` y verificar que las tablas `offset_storage` y `schema_history` existen y se están poblando.
- Re-ejecutar `minikube/scripts/rto_experiment.sh 3` y confirmar que el RTO observado se mantiene en el rango ya medido (~5–6s `time-to-first-event`, ~22s `time-to-Ready`).
- Confirmar no-duplicación: el `cdc-sink` no emite eventos reprocesados tras restarts.

## Capabilities

### Modified Capabilities
- `debezium-server-ha`: se refina el Requirement "Durabilidad del offset y schema history" para reflejar el cambio de PVC-file a MySQL-JDBC. Se agregan Requirements nuevos sobre la presencia y aislamiento de `mysql-debezium-state` por stack y sobre la disponibilidad de `debezium-storage-jdbc` en la imagen de cada stack.

## Impact

- **Manifests Kubernetes:** se modifican `01-configmaps.yaml`, `02-secrets.yaml` y `06-debezium-server.yaml` en ambos stacks. Se agrega un nuevo manifest `04a-mysql-debezium-state.yaml` por stack. El PVC `debezium-data` se elimina del manifest (en cluster ya existente, se borra a mano con `kubectl delete pvc debezium-data -n <ns>` después de aplicar — está cubierto en `tasks.md`).
- **Imágenes:** se construye una imagen custom nueva (`withreplica/debezium-server-mysql57-jdbc:2.4.2.Final`) vía `minikube/Makefile`. El stack mysql8 no requiere cambio de imagen.
- **Documentación / specs:** se modifica un Requirement y se agregan tres a la capability `debezium-server-ha` (no se crea capability nueva: el "estado" sigue siendo parte de la HA del servidor Debezium).
- **Operación:** la migración es **greenfield** — al cambiar de backing store, el offset viejo no se importa. Debezium hará un nuevo snapshot inicial de `inventory.customers` la primera vez (es trivial en el lab: pocas filas, segundos). Esto se documenta en `tasks.md` y se acepta explícitamente. Si más adelante se quiere migrar offsets reales en producción, se hará con un script separado fuera de este change.
- **Dependencias externas:** descarga de `debezium-storage-jdbc-2.4.2.Final.jar` desde `repo1.maven.org` durante el `docker build` (mismo patrón que la imagen 3.5 ya hace con el conector MySQL). Ninguna otra.

## Aplicabilidad a producción

Todo este cambio está en la categoría `production-relevant` con un matiz: en producción habrá **un solo** `mysql-debezium-state` externo (no en k8s) — el patrón es idéntico, pero el manifest del Pod no aplica allá. El contrato (Debezium escribe a una DB dedicada para state) sí se traslada tal cual. La construcción de la imagen custom para 5.7 también es production-relevant si en producción se usa Debezium 2.4 contra una DB MySQL legacy.
