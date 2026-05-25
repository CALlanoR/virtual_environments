# Conectarse al lab desde el host: DBeaver y binlog

Guía operativa para inspeccionar los componentes del lab consolidado (`cdc-lab`) desde tu máquina local. Cubre dos tareas comunes:

1. Conectarse al MySQL `mysql-debezium-state` (donde Debezium guarda offset + schema history) desde DBeaver para inspeccionar las tablas de estado.
2. Ver el binlog de cada `mysql-replica-*` — vía SQL desde DBeaver, o cruda con `mysqlbinlog` desde el Pod.

Pre-requisitos: minikube corriendo, namespace `cdc-lab` levantado (`make -C minikube up`), DBeaver instalado en el host.

---

## A. Conectarse a `mysql-debezium-state` desde DBeaver

El Service `mysql-debezium-state` es `ClusterIP` (no expone NodePort a propósito — es estado interno). Para acceder desde tu host hay que abrir un túnel con `kubectl port-forward`.

### 1. Levantar el port-forward

Déjalo corriendo en una terminal aparte mientras uses DBeaver:

```bash
kubectl port-forward -n cdc-lab svc/mysql-debezium-state 3307:3306
```

Mapea `localhost:3307` (host) → `mysql-debezium-state:3306` (cluster). Uso 3307 en lugar de 3306 para no chocar con un MySQL que tengas instalado localmente. Mientras el comando esté corriendo, la conexión está activa; al hacer `Ctrl+C` se cierra.

### 2. Sacar los passwords del Secret

```bash
# Root (para administrar el Pod)
kubectl get secret -n cdc-lab debezium-state-credentials \
  -o jsonpath='{.data.root-password}' | base64 -d ; echo

# Usuario del stack 5.7 (solo ve dbz_state_57)
kubectl get secret -n cdc-lab debezium-state-credentials \
  -o jsonpath='{.data.dbz-state-57-password}' | base64 -d ; echo

# Usuario del stack 8 (solo ve dbz_state_8)
kubectl get secret -n cdc-lab debezium-state-credentials \
  -o jsonpath='{.data.dbz-state-8-password}' | base64 -d ; echo
```

### 3. Configurar la conexión en DBeaver

| Campo | Valor |
|---|---|
| **Driver** | MySQL (no MariaDB) |
| **Server Host** | `localhost` |
| **Port** | `3307` |
| **Database** | dejar en blanco si vas como root; `dbz_state_57` o `dbz_state_8` si vas como ese usuario |
| **Username** | `root`, o `dbz_state_57`, o `dbz_state_8` |
| **Password** | el que sacaste del Secret en el paso 2 |
| **Driver properties → `allowPublicKeyRetrieval`** | `true` |
| **Driver properties → `useSSL`** | `false` |

`allowPublicKeyRetrieval=true` y `useSSL=false` son los mismos parámetros que usa Debezium internamente; sin ellos vas a ver `Public Key Retrieval is not allowed`.

### 4. Queries útiles una vez conectado

Como `root`:

```sql
SHOW DATABASES;
-- dbz_state_57, dbz_state_8, information_schema, mysql, performance_schema, sys

-- Últimos offsets persistidos por cada Debezium
SELECT id, offset_key, offset_val, record_insert_ts
FROM dbz_state_57.offset_storage
ORDER BY record_insert_ts DESC LIMIT 5;

-- Schema history (resumen para no inundar la pantalla)
SELECT id, LEFT(history_data, 80) AS history_preview, record_insert_ts
FROM dbz_state_8.schema_history
ORDER BY record_insert_ts, record_insert_seq DESC LIMIT 10;

-- Verificar aislamiento de usuarios (esta query debe FALLAR con `command denied`
-- cuando estás conectado como dbz_state_57 y consultas dbz_state_8):
-- SELECT * FROM dbz_state_8.offset_storage LIMIT 1;
```

---

## B. Ver el binlog de cada `mysql-replica-*`

Hay dos formas, según qué tan crudo quieras verlo. Las dos requieren acceso al Pod del replica.

### Vía A — Desde DBeaver (queries SQL)

Los dos `mysql-replica-*` exponen NodePort. Útil si quieres ver el binlog con interfaz gráfica.

```bash
minikube ip
# devuelve algo tipo 192.168.49.2
```

Conexiones DBeaver:

| Stack | Host | Port | User / Password |
|---|---|---|---|
| `mysql-replica-57` | `<minikube ip>` | `30407` | `root` / `root` (default del lab) |
| `mysql-replica-8` | `<minikube ip>` | `30409` | `root` / `root` |

> Si prefieres no usar NodePort, port-forward funciona igual:
> ```bash
> kubectl port-forward -n cdc-lab svc/mysql-replica-57 3308:3306
> ```
> y conectas a `localhost:3308`.

Una vez conectado, los comandos SQL útiles:

```sql
-- Lista todos los binlogs que el replica tiene en disco
SHOW BINARY LOGS;
-- mysql-bin.000001 | 154
-- mysql-bin.000002 | 12345
-- mysql-bin.000003 | 3897421

-- Posición actual de escritura del binlog del replica
SHOW MASTER STATUS;
-- File: mysql-bin.000003 | Position: 3897421 | GTID: ...

-- Estado de la replicación primary→replica (necesario para que Debezium lea)
SHOW REPLICA STATUS\G          -- en MySQL 8
SHOW SLAVE  STATUS\G            -- en MySQL 5.7
-- Mira: Replica_IO_Running=Yes, Replica_SQL_Running=Yes, Seconds_Behind_Source=0

-- Ver eventos de un binlog específico (los más recientes son los más útiles)
SHOW BINLOG EVENTS IN 'mysql-bin.000003' LIMIT 50;
SHOW BINLOG EVENTS IN 'mysql-bin.000003' FROM 3800000 LIMIT 100;
-- Columnas: Log_name | Pos | Event_type | Server_id | End_log_pos | Info
-- Event_type interesante: Write_rows, Update_rows, Delete_rows, Xid, Query
```

`SHOW BINLOG EVENTS` muestra los eventos pero no el contenido de las filas. Para ver las filas reales necesitas la Vía B.

### Vía B — Desde el Pod, con `mysqlbinlog` (vista cruda)

`mysqlbinlog` es el parser oficial y muestra todo, incluyendo las filas afectadas (en `binlog_row_image: FULL`, que es como está configurado el lab).

```bash
# Listar los binlogs físicamente disponibles en el disco del replica 5.7
kubectl exec -n cdc-lab mysql-replica-57-0 -- ls -lh /var/lib/mysql/ | grep mysql-bin

# Volcar el más reciente, decodificado (formato legible)
kubectl exec -n cdc-lab mysql-replica-57-0 -- \
  mysqlbinlog --base64-output=DECODE-ROWS --verbose /var/lib/mysql/mysql-bin.000003 | less

# Solo las últimas ~50 filas afectadas (filtrando lo demás)
kubectl exec -n cdc-lab mysql-replica-57-0 -- \
  mysqlbinlog --base64-output=DECODE-ROWS --verbose /var/lib/mysql/mysql-bin.000003 \
  | grep -E "^(### |# at |#[0-9])" | tail -100

# Lo mismo para el stack 8 (cambia el Pod)
kubectl exec -n cdc-lab mysql-replica-8-0 -- \
  mysqlbinlog --base64-output=DECODE-ROWS --verbose /var/lib/mysql/mysql-bin.000003 | less
```

`--base64-output=DECODE-ROWS --verbose` decodifica los eventos `ROW` (que son los que Debezium consume) en pseudo-SQL legible. Sin esos flags, ves los eventos como blobs base64 inútiles.

Ejemplo de output decodificado:

```
### UPDATE `inventory`.`customers`
### WHERE
###   @1=42        /* INT meta=0 nullable=0 is_null=0 */
###   @2='Donald'  /* VARSTRING(400) meta=400 nullable=0 is_null=0 */
###   ...
### SET
###   @1=42
###   @2='Donald'
###   @4='donald.knuth555@example.com'
```

Esos `### UPDATE`/`### INSERT`/`### DELETE` son **exactamente** lo que Debezium lee y transforma en los eventos JSON que llegan al sink. Útil cuando quieres confirmar que un cambio en el primary se reflejó en el replica antes de que Debezium lo emitiera.

### Atajo de shell

```bash
# Pega esto en tu ~/.bashrc para tener una función `binlog`
binlog() {
  local stack="${1:?usage: binlog <57|8> [binlog-file]}"
  local file="${2:-mysql-bin.000003}"
  kubectl exec -n cdc-lab "mysql-replica-${stack}-0" -- \
    mysqlbinlog --base64-output=DECODE-ROWS --verbose "/var/lib/mysql/${file}" | less
}
# Uso: binlog 57          o   binlog 8 mysql-bin.000005
```

---

## Troubleshooting

| Síntoma | Causa probable | Cómo arreglar |
|---|---|---|
| DBeaver: `Public Key Retrieval is not allowed` | Driver properties no tienen `allowPublicKeyRetrieval=true` | Agregar en Driver properties: `allowPublicKeyRetrieval=true` y `useSSL=false` |
| DBeaver: `Communications link failure` al conectar a localhost:3307 | El `kubectl port-forward` no está corriendo, o se cerró | Volver a ejecutar `kubectl port-forward -n cdc-lab svc/mysql-debezium-state 3307:3306` |
| DBeaver: `Access denied for user 'dbz_state_57'` cuando consultas `dbz_state_8` | Aislamiento funcionando correctamente | No es un bug — usa el usuario `dbz_state_8` (o `root`) para esa DB |
| `SHOW BINLOG EVENTS` retorna vacío | Estás consultando un binlog que no existe, o no hubo eventos en ese rango | `SHOW BINARY LOGS` para listar los disponibles y elegir el correcto |
| `kubectl exec` no encuentra `mysqlbinlog` | El Pod está en otra fase (`Init` o `Pending`) | `kubectl get pods -n cdc-lab` para confirmar que `mysql-replica-*-0` está `Running` |
| Los binlogs ocupan mucho espacio en el PVC | Política de expiración demasiado laxa | El stack 5.7 usa `expire_logs_days=1`; el stack 8 usa `binlog_expire_logs_seconds=86400`. Ambos limpian binlogs >1 día automáticamente. |
