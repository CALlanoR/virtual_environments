# Tablas de estado de Debezium (`offset_storage` y `schema_history`)

Tablas que Debezium usa para persistir su estado interno cuando se configura el JDBC store para guardar en base de datos, en este caso en mysql, el cual es una copia de seguridad si se cae el servidor.

---

## Tabla `offset_storage`

Guarda **dónde se quedó** el conector leyendo el binlog. Es el "bookmark" de Debezium — si el conector se reinicia, retoma desde aquí.

| Columna | Significado |
|---|---|
| **`id`** | UUID generado por el JDBC offset store. Identificador único de cada fila de offset escrita. No es semántico, solo PK. |
| **`offset_key`** | Clave que identifica al conector. Ejemplo: `["http",{"server":"replica-cdc-57"}]` — el `server` es el `topic.prefix` / `database.server.name` del conector. El `"http"` viene del prefijo interno que Kafka Connect usa para este store. |
| **`offset_val`** | El offset propiamente dicho — JSON con la posición exacta del binlog donde Debezium debe reanudar. Detalle abajo. |
| **`record_insert_ts`** | Timestamp del momento en que esta fila se escribió en MySQL. Útil para ver qué tan reciente es el último commit de offset. |
| **`record_insert_seq`** | Contador secuencial de escrituras. Cada vez que Debezium "flushea" el offset, este número incrementa (`103` = se ha flusheado 103 veces). |

### Desglose del JSON de `offset_val`

```json
{
  "transaction_id": null,
  "ts_sec": 1778814507,
  "file": "mysql-bin.000003",
  "pos": 3737303,
  "gtids": "1328ac24-...:1-2456,22003d25-...:1-5",
  "row": 1,
  "server_id": 1,
  "event": 2
}
```

- **`transaction_id`**: ID de transacción XA si aplica (normalmente `null` en MySQL).
- **`ts_sec`**: timestamp en segundos del último evento procesado del binlog.
- **`file`**: archivo de binlog actual del master (`mysql-bin.000003`).
- **`pos`**: byte-offset dentro de ese archivo donde quedó el cursor.
- **`gtids`**: conjunto de GTIDs ya consumidos. Cada UUID corresponde a un `server_uuid` distinto (probablemente master + replica). El rango `1-2456` significa "ya procesé las transacciones 1 a 2456 de ese servidor".
- **`row`**: índice de fila dentro de un evento multi-row (cuando un INSERT/UPDATE afecta varias filas en un solo evento del binlog).
- **`server_id`**: `server_id` de MySQL desde el que se leyó el evento.
- **`event`**: contador interno de eventos dentro de la transacción actual.

---

## Tabla `schema_history`

Guarda el **historial de DDL** (CREATE, ALTER, DROP). Debezium necesita esto porque cuando lee un evento antiguo del binlog tiene que saber cómo era el esquema en ese momento para deserializar las filas correctamente.

| Columna | Significado |
|---|---|
| **`id`** | UUID único por entrada DDL. PK técnica. |
| **`history_data`** | JSON con la sentencia DDL y metadata. Detalle abajo. |
| **`history_data_seq`** | Secuencia interna cuando un DDL grande se parte en varios chunks. Normalmente `0` porque cada DDL cabe en una sola fila. |
| **`record_insert_ts`** | Cuándo se insertó la fila. |
| **`record_insert_seq`** | Orden cronológico en que ocurrieron los DDL. Es la columna clave para reconstruir la historia. |

### Orden real de los DDL (ordenado por `record_insert_seq`)

| seq | DDL | Qué hace |
|---|---|---|
| 1 | `SET character_set_server=latin1...` | Sets de sesión iniciales del snapshot |
| 2 | `DROP TABLE IF EXISTS inventory.audit_log` | Limpieza previa |
| 3 | `DROP TABLE IF EXISTS inventory.customers` | Limpieza previa |
| 4 | `DROP DATABASE IF EXISTS inventory` | Limpieza previa |
| 5 | `CREATE DATABASE inventory` | Recrea DB |
| 6 | `USE inventory` | Cambia de contexto |
| 7 | `CREATE TABLE audit_log (...)` | Crea tabla con `id`, `message`, `created_at` |
| 8 | `CREATE TABLE customers (...)` | Crea tabla con `id`, `first_name`, `last_name`, `email` |

> Los `DROP` aparecen aunque la BD esté limpia porque el snapshot inicial de Debezium en modo `schema_only_recovery` / `initial` reconstruye el árbol DDL completo para tener el esquema canónico.

### Desglose del JSON de `history_data`

```json
{
  "source": {"server": "replica-cdc-57"},
  "position": {
    "ts_sec": 1778813161,
    "file": "mysql-bin.000003",
    "pos": 2950450,
    "gtids": "...",
    "snapshot": true
  },
  "ts_ms": 1778813161669,
  "databaseName": "inventory",
  "ddl": "CREATE TABLE ...",
  "tableChanges": [ ... ]
}
```

- **`source.server`**: `topic.prefix` del conector. Permite separar historia de varios conectores que compartan la tabla.
- **`position`**: posición del binlog en el momento del DDL (mismos campos que `offset_val`).
  - **`snapshot: true`** → este DDL se capturó durante el snapshot inicial, no en streaming en vivo.
- **`ts_ms`**: timestamp en milisegundos cuando Debezium procesó el DDL.
- **`databaseName`**: BD afectada (vacío en el primer DDL porque es global de sesión).
- **`ddl`**: la sentencia SQL exacta tal como vino del binlog/snapshot.
- **`tableChanges`**: representación estructurada del cambio para que Debezium no tenga que re-parsear el SQL al reanudar. Contiene:
  - `type`: `CREATE`, `ALTER`, `DROP`.
  - `id`: nombre cualificado de la tabla.
  - `table.columns[]`: cada columna con su `jdbcType` (4=INT, 12=VARCHAR, 93=DATETIME), `typeName`, `length`, `position`, `optional`, `autoIncremented`, `defaultValueExpression`, etc.
  - `table.primaryKeyColumnNames`: PK.

---

## En conclusion:

- **`offset_storage`** → "¿desde dónde sigo leyendo?" (1 sola fila viva, se sobrescribe).
- **`schema_history`** → "¿cómo era el esquema en cualquier momento del pasado?" (append-only, una fila por DDL).

Si borras `offset_storage`, el conector hace snapshot de nuevo. Si borras `schema_history`, no podrá deserializar binlog antiguo y romperá — solo se regenera con un snapshot inicial completo.
