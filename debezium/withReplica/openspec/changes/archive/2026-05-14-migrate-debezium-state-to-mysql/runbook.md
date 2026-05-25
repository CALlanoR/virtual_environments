# Runbook — Migrate Debezium state (offset + schema history) to dedicated MySQL

Bitácora paso a paso de la implementación del change `migrate-debezium-state-to-mysql`. Ejecutado el `2026-05-14`. Reproducible desde cero por otra persona sin contexto previo.

## 1. Estado de partida

Ambos stacks `cdc-mysql57` y `cdc-mysql8` arriba con la config heredada del change `2026-05-14-evaluate-debezium-server-ha`: `debezium-server` con probes httpGet a `/q/health/{live,ready}:8080`, `FileOffsetBackingStore` y `FileSchemaHistory` apuntando a `/debezium/data/{offsets.dat,schema-history.dat}` montado desde el PVC `debezium-data` (RWO, 100Mi).

## 2. Task 1.1 — Esquemas de las tablas

Verificación inspeccionando el bytecode de `JdbcOffsetBackingStoreConfig` y `JdbcSchemaHistoryConfig` en los dos JAR:

```bash
kubectl cp -n cdc-mysql8 $(kubectl get pod -n cdc-mysql8 -l app=debezium-server -o jsonpath='{.items[0].metadata.name}'):/debezium/lib/debezium-storage-jdbc-3.5.0.Final.jar /tmp/dbz-jars/storage-jdbc-3.5.0.jar
curl -fsSLo /tmp/dbz-jars/storage-jdbc-2.4.2.jar https://repo1.maven.org/maven2/io/debezium/debezium-storage-jdbc/2.4.2.Final/debezium-storage-jdbc-2.4.2.Final.jar
for V in 3.5.0 2.4.2; do
  unzip -p /tmp/dbz-jars/storage-jdbc-$V.jar io/debezium/storage/jdbc/offset/JdbcOffsetBackingStoreConfig.class | strings | grep -E 'CREATE TABLE'
done
```

Hallazgo: los DDLs por defecto son casi idénticos entre 2.4.2 y 3.5.0; solo 3.5.0 declara `PRIMARY KEY` explícito. Pre-creando con PK explícito, **un solo `initdb` sirve para ambos stacks**. Anotado en `design.md` Decisión 7 y Open Question 1.

## 3. Task 1.2 — JAR en Maven

```bash
curl -fsI https://repo1.maven.org/maven2/io/debezium/debezium-storage-jdbc/2.4.2.Final/debezium-storage-jdbc-2.4.2.Final.jar
```

→ `HTTP/2 200`, `content-length: 22679`. Disponible.

## 4. Section 2 — Imagen custom para mysql5.7

### 4.1 Dockerfile

Archivo: `minikube/images/debezium-server-mysql57-jdbc/Dockerfile`. Multi-stage: alpine baja el JAR de Maven, stage final extiende `debezium/server:2.4.2.Final` y copia el JAR a `/debezium/lib/`. Patrón idéntico al `docker-compose/mysql8/debezium/Dockerfile` existente.

### 4.2 Makefile

Targets añadidos en `minikube/Makefile`:

```
image-build-57    docker build de la imagen custom para 5.7
image-load-57     minikube image load
image-unload-57   minikube image rm
image-clean-57    image-unload-57 + docker image rm
```

Y `up-5.7` ahora depende de `image-load-57` (simetría con `up-8` → `image-load`).

### 4.3 Build + load

```bash
cd minikube && make image-build-57 && make image-load-57
docker run --rm withreplica/debezium-server-mysql57-jdbc:2.4.2.Final ls /debezium/lib/ | grep storage-jdbc
# → debezium-storage-jdbc-2.4.2.Final.jar  ✓
```

## 5. Sections 3 + 4 — Manifests del state-store + Secrets

Archivo nuevo `minikube/mysql{5.7,8}/04a-mysql-debezium-state.yaml` con 4 recursos (PVC 500Mi, ConfigMap initdb, Service ClusterIP, Deployment con `mysql:5.7` o `mysql:8.0`). Initdb crea DB `dbz_state`, usuario `dbz_state` con plugin `mysql_native_password` y tablas `offset_storage` + `schema_history` con esquema verificado.

Secrets generados con `openssl rand -base64 32`. Archivo `minikube/mysql{5.7,8}/02-secrets.yaml` extendido con un Secret `debezium-state-credentials` con keys `root-password` y `dbz-state-password`.

```bash
DBZ_PW=$(openssl rand -base64 32 | tr -d '\n')
ROOT_PW=$(openssl rand -base64 32 | tr -d '\n')
```

## 6. Sections 5 + 6 — Config + Deployment

`debezium-config` ConfigMap pasa de:

```properties
debezium.source.offset.storage=org.apache.kafka.connect.storage.FileOffsetBackingStore
debezium.source.offset.storage.file.filename=/debezium/data/offsets.dat
debezium.source.schema.history.internal=io.debezium.storage.file.history.FileSchemaHistory
debezium.source.schema.history.internal.file.filename=/debezium/data/schema-history.dat
```

a:

```properties
debezium.source.offset.storage=io.debezium.storage.jdbc.offset.JdbcOffsetBackingStore
debezium.source.offset.storage.jdbc.url=jdbc:mysql://mysql-debezium-state:3306/dbz_state?useSSL=false
debezium.source.offset.storage.jdbc.user=dbz_state
debezium.source.offset.storage.jdbc.offset.table.name=offset_storage
debezium.source.schema.history.internal=io.debezium.storage.jdbc.history.JdbcSchemaHistory
debezium.source.schema.history.internal.jdbc.url=jdbc:mysql://mysql-debezium-state:3306/dbz_state?useSSL=false
debezium.source.schema.history.internal.jdbc.user=dbz_state
debezium.source.schema.history.internal.jdbc.schema.history.table.name=schema_history
```

Los passwords NO viven en el ConfigMap. Se inyectan via env vars en el Deployment (`DEBEZIUM_SOURCE_OFFSET_STORAGE_JDBC_PASSWORD` y `DEBEZIUM_SOURCE_SCHEMA_HISTORY_INTERNAL_JDBC_PASSWORD`, ambos `valueFrom.secretKeyRef`). Quarkus interpreta esos nombres como overrides de las properties homólogas.

El Deployment `debezium-server`:
- Quita `volumeMount /debezium/data` y el `volume data`.
- Quita el `PersistentVolumeClaim debezium-data`.
- Agrega las dos env vars descritas arriba.
- En mysql5.7: cambia la `image` a `withreplica/debezium-server-mysql57-jdbc:2.4.2.Final`. En mysql8: mantiene `withreplica/debezium-server-mysql:3.5.0.Final`.
- Probes, replicas, strategy, resources, ConfigMap mount sin cambios.

## 7. Section 7 — Aplicación y verificación

```bash
# mysql57
kubectl apply -f minikube/mysql5.7/02-secrets.yaml
kubectl apply -f minikube/mysql5.7/04a-mysql-debezium-state.yaml
kubectl rollout status deployment/mysql-debezium-state -n cdc-mysql57 --timeout=180s
kubectl apply -f minikube/mysql5.7/01-configmaps.yaml
kubectl apply -f minikube/mysql5.7/06-debezium-server.yaml
# mysql8 — repetir con los mismos pasos
```

Verificación de tablas pobladas:

```bash
for NS in cdc-mysql57 cdc-mysql8; do
  ROOT=$(kubectl get secret -n "$NS" debezium-state-credentials -o jsonpath='{.data.root-password}' | base64 -d)
  kubectl exec -n "$NS" deploy/mysql-debezium-state -- mysql -uroot -p"$ROOT" -e \
    "SELECT 'offset_storage' tbl, COUNT(*) FROM dbz_state.offset_storage UNION ALL SELECT 'schema_history', COUNT(*) FROM dbz_state.schema_history;"
done
```

Resultado: ambos stacks reportan `offset_storage`=1 y `schema_history`=8 tras el snapshot inicial. Borrado de los PVC viejos `debezium-data` en ambos namespaces: confirmado.

## 8. Tropiezos durante la implementación

Tres bugs encontrados y resueltos durante la aplicación. **Todos documentados aquí porque son los que más tiempo cuestan si alguien repite el ejercicio.**

### 8.1 `${env:VAR}` no expandido por Debezium 2.4

Primer intento: poner `debezium.source.offset.storage.jdbc.password=${env:DBZ_STATE_PASSWORD}` en el ConfigMap y una env var `DBZ_STATE_PASSWORD` en el Deployment. Debezium 2.4 **no** expande esa sintaxis y pasa la string literal al driver MySQL → `Access denied for user 'dbz_state'`.

**Solución**: usar el mecanismo estándar de Quarkus para overrides por env var. Quitar la línea `*.password=` del ConfigMap (queda undefined ahí) y agregar al Deployment una env var con el nombre derivado de la property: `DEBEZIUM_SOURCE_OFFSET_STORAGE_JDBC_PASSWORD` para `debezium.source.offset.storage.jdbc.password`. Quarkus la lee con precedencia sobre `application.properties`. Verificado funciona en 2.4 y 3.5.

### 8.2 `caching_sha2_password` y `Public Key Retrieval is not allowed`

MySQL 8 crea usuarios por defecto con `caching_sha2_password`, que requiere SSL o `allowPublicKeyRetrieval=true` en el JDBC URL para el handshake. mysql5.7 usa `mysql_native_password` por defecto, sin problema.

**Solución**: crear el usuario `dbz_state` explícitamente con `IDENTIFIED WITH mysql_native_password BY '...'` (alineado con cómo el resto del lab crea `repl` y `debezium`). Aplicado tanto en `CREATE USER` del initdb como en el `ALTER USER` que actualiza el password al valor del Secret. Un solo initdb sirve para ambos stacks porque `mysql_native_password` está disponible en 5.7 y 8.

### 8.3 `Column length too big for column 'history_data' (max = 16383)`

MySQL 8 con utf8mb4 (default) limita `VARCHAR(N)` a 16383 caracteres porque cada char ocupa hasta 4 bytes y el límite de fila es 65535. Mi pre-create usaba `VARCHAR(65000)` (alineado con el `DEFAULT_TABLE_DDL` de Debezium), que falla en MySQL 8. mysql5.7 con latin1 default lo aceptaba.

**Solución**: cambiar `history_data` a `MEDIUMTEXT` (hasta 16MB). Los tipos TEXT/BLOB se almacenan off-row y no cuentan contra el row-size. Debezium hace `CREATE TABLE IF NOT EXISTS` con `VARCHAR(65000)` en su DDL hardcoded, pero como la tabla ya existe, esa sentencia es no-op y la columna sigue siendo `MEDIUMTEXT`.

### 8.4 `CREATE command denied` (privilegio CREATE faltante)

Aunque pre-creamos las tablas, `JdbcSchemaHistory` llama `CREATE TABLE IF NOT EXISTS schema_history` al arrancar Debezium **siempre** (incluso si la tabla ya está). Eso requiere `CREATE` privilege en el usuario. Mi grant original era solo `SELECT, INSERT, UPDATE, DELETE` (la Decisión 5 del design lo justificaba como "privilegio mínimo").

**Solución**: agregar `CREATE` al grant. Final: `GRANT SELECT, INSERT, UPDATE, DELETE, CREATE ON dbz_state.* TO 'dbz_state'@'%'`. Esto relaja parcialmente la Decisión 5 del design (justificado en sección "Discrepancias respecto al design original" abajo).

## 9. Section 8 — Re-medición de RTO

`minikube/scripts/rto_experiment.sh 3` ejecutado con la nueva config en ambos stacks. CSV completo en `/tmp/rto_results_*.csv`.

### Tabla de regresión

| Stack | TTR (mediana) baseline → JDBC | TTFE (mediana) baseline → JDBC | Δ TTR | Δ TTFE |
|---|---|---|---|---|
| `cdc-mysql8` | 22.24s → 22.32s | 5.52s → 5.90s | +0.36% | +6.9% |
| `cdc-mysql57` | 22.16s → 22.37s | 6.11s → 6.28s | +0.95% | +2.8% |

Todas las desviaciones < 10% del umbral acordado. **No hay regresión**. El cambio de file-backing-store a JDBC-backing-store no degrada el RTO observable.

### No-duplicación

Inspección del log del sink en ambos stacks: ningún `(file, pos)` (mysql57) ni GTID (mysql8) aparece dos veces. Debezium reanuda limpiamente desde el offset persistido en `dbz_state.offset_storage` tras cada `kubectl delete pod`.

## 10. Discrepancias respecto al design original

### 10.1 Decisión 5 — privilegios del usuario

El design dijo "sin CREATE ni DROP post-bootstrap". La realidad es que Debezium llama `CREATE TABLE IF NOT EXISTS` cada vez que arranca, así que necesita CREATE. El grant final es `SELECT, INSERT, UPDATE, DELETE, **CREATE**`. **Sigue sin tener** `DROP, ALTER, INDEX, GRANT OPTION, FILE, SUPER`. El espíritu del privilegio mínimo se conserva: el usuario no puede borrar tablas, alterar esquemas, ni escalar privilegios.

### 10.2 Decisión 7 — tipo de `history_data`

El design fijó `VARCHAR(65000)` alineado con el `DEFAULT_TABLE_DDL` de Debezium. La realidad es que ese tipo falla en MySQL 8 con utf8mb4. El initdb final usa `MEDIUMTEXT`. Funcionalmente equivalente para Debezium (el contenido entra), y más portable entre versiones de MySQL.

### 10.3 Decisión 8 — sintaxis de propagación del password

El design dijo `${env:DBZ_STATE_PASSWORD}` en `application.properties`. La realidad es que Debezium 2.4 no expande esa sintaxis. Se usa el otro mecanismo de Quarkus: nombres de env vars derivados de las properties (Quarkus convierte automáticamente). El password sigue viviendo en un Secret y se inyecta solo como env var, nunca en el ConfigMap.

## 11. Rollback

Si en algún momento hay que volver al state-backing en file:

1. `kubectl apply -f` de la versión pre-migration de `01-configmaps.yaml` y `06-debezium-server.yaml`. Eso restaura el ConfigMap a `FileOffsetBackingStore` / `FileSchemaHistory` y recrea el `PersistentVolumeClaim debezium-data` con su mount.
2. `kubectl rollout status deployment/debezium-server -n <ns>` por stack. Al levantar, Debezium **no encuentra** el offset file (es PVC nuevo), entra en `snapshot.mode=initial` y re-snapshotea `inventory.customers`. Aceptable en el lab; documentar como evento al consumidor del sink.
3. Opcional: borrar el state-store con `kubectl delete -f minikube/mysql<v>/04a-mysql-debezium-state.yaml`. Eso elimina Deployment, Service, ConfigMap y el PVC `debezium-state-data`. El Secret `debezium-state-credentials` se queda; borrarlo a mano si se quiere limpieza total.

**Costo del rollback**: una ventana de indisponibilidad por stack (~30s del `Recreate` + el snapshot inicial, segundos para nuestras pocas filas) y un evento de re-snapshot visible al sink.

## 12. Anexo — Troubleshooting

| Síntoma | Causa más probable | Cómo confirmar | Cómo arreglar |
|---|---|---|---|
| `Access denied for user 'dbz_state'` | El password literal en lugar de la env var | Buscar en logs `jdbc.password=DBZ_STATE_PASSWORD` (no `********`) | Verificar que el Deployment tiene las dos env vars `DEBEZIUM_SOURCE_OFFSET_STORAGE_JDBC_PASSWORD` y `DEBEZIUM_SOURCE_SCHEMA_HISTORY_INTERNAL_JDBC_PASSWORD` y que el Secret existe |
| `Public Key Retrieval is not allowed` | Usuario con `caching_sha2_password` en MySQL 8 | `SELECT plugin FROM mysql.user WHERE user='dbz_state'` | `ALTER USER 'dbz_state'@'%' IDENTIFIED WITH mysql_native_password BY '<pw>'` |
| `CREATE command denied to user 'dbz_state'` | Falta privilegio CREATE | `SHOW GRANTS FOR 'dbz_state'@'%'` | `GRANT CREATE ON dbz_state.* TO 'dbz_state'@'%'` |
| `Column length too big for column 'history_data'` | `VARCHAR(65000)` en MySQL 8 utf8mb4 | `DESCRIBE schema_history` muestra VARCHAR | `ALTER TABLE schema_history MODIFY history_data MEDIUMTEXT` |
| Tabla `schema_history` no existe en mysql8 después del initdb | El initdb crasheó silenciosamente por el row-size; el container terminó la init sin emitir error visible | `SHOW TABLES FROM dbz_state` | Crear la tabla manualmente con `MEDIUMTEXT` (ver SQL en sección 8.3) o re-iniciar el state-store con el PVC limpio tras corregir el initdb |
| `mysql-debezium-state` pod queda en `Pending` | PVC no se puede provisionar | `kubectl describe pvc debezium-state-data -n <ns>` | Verificar StorageClass; en minikube default es `standard` |

## 13. Regeneración de passwords

Si se compromete o expira un password:

```bash
NEW_PW=$(openssl rand -base64 32 | tr -d '\n')
# 1. Actualizar el Secret
kubectl create secret generic debezium-state-credentials \
  -n cdc-mysql8 \
  --from-literal=root-password="<root_pw_existente>" \
  --from-literal=dbz-state-password="$NEW_PW" \
  --dry-run=client -o yaml | kubectl apply -f -
# 2. Actualizar el usuario en el MySQL del state-store
ROOT=$(kubectl get secret -n cdc-mysql8 debezium-state-credentials -o jsonpath='{.data.root-password}' | base64 -d)
kubectl exec -n cdc-mysql8 deploy/mysql-debezium-state -- mysql -uroot -p"$ROOT" -e \
  "ALTER USER 'dbz_state'@'%' IDENTIFIED WITH mysql_native_password BY '$NEW_PW'; FLUSH PRIVILEGES;"
# 3. Forzar reinicio del Deployment para que tome la nueva env var
kubectl rollout restart deployment/debezium-server -n cdc-mysql8
```

Repetir para `cdc-mysql57`.
