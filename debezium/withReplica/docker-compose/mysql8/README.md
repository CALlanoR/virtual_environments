# Stack `mysql8/` — MySQL 8.0 + Debezium Server 3.5.0.Final

Variante moderna del escenario "Debezium leyendo binlogs de la réplica". Se ejecuta de forma independiente del stack [`mysql5.7/`](../mysql5.7/README.md) — pueden coexistir.

## Topología

```
┌──────────────┐  replicación   ┌──────────────┐  binlog   ┌──────────────────┐  HTTP POST   ┌──────────┐
│ mysql-primary│ ─────────────▶│ mysql-replica│ ─────────▶│ debezium-server  │ ───────────▶│ cdc-sink │
│  :3308 host  │   (GTID, ROW) │  :3309 host  │ (lee aquí)│ (3.5 desde quay) │  evento JSON │ (stdout) │
└──────────────┘                └──────────────┘            └──────────────────┘              └──────────┘
       ▲ escrituras                  read_only=ON                                                docker compose
       │                              log_replica_updates=ON                                     logs -f cdc-sink
   tu cliente
```

Diferencias clave respecto al stack 5.7:

| Concepto | mysql5.7 | mysql8 |
| --- | --- | --- |
| MySQL | `mysql:5.7` | `mysql:8.0` |
| Debezium | `debezium/server:2.4.2.Final` (Docker Hub) | **`quay.io/debezium/server:3.5.0.Final`** |
| Sintaxis de replicación | `CHANGE MASTER TO` / `START SLAVE` / `SHOW SLAVE STATUS` | `CHANGE REPLICATION SOURCE TO` / `START REPLICA` / `SHOW REPLICA STATUS` |
| Variable de re-logging | `log_slave_updates` | `log_replica_updates` |
| Plugin de auth de usuarios | default 5.7 | `mysql_native_password` declarado explícitamente (default en 8.0 es `caching_sha2_password`) |
| Puertos host | 3306 / 3307 | **3308 / 3309** |

## Pre-requisitos

- Docker Engine 20.10+ y Docker Compose v2.
- Puertos host **3308** y **3309** libres.
- Acceso a `quay.io` para tirar la imagen de Debezium 3.5 (anónimo, sin login).

## Levantar

```bash
docker compose up -d
docker compose ps
```

Healthchecks encadenados:
1. `mysql-primary` → init scripts (usuarios + schema).
2. `mysql-replica` → init `CHANGE REPLICATION SOURCE TO + START REPLICA`. Healthcheck valida `Replica_IO_Running` y `Replica_SQL_Running`.
3. `cdc-sink` arranca en paralelo.
4. `debezium-server` arranca cuando réplica + sink están listos.

## Verificar replicación

```bash
mysql -h 127.0.0.1 -P 3309 -uroot -proot \
  -e 'SHOW REPLICA STATUS\G' | grep -E 'Replica_(IO|SQL)_Running|Last_Error'
```

Esperado: `Replica_IO_Running: Yes` y `Replica_SQL_Running: Yes`.

```bash
mysql -h 127.0.0.1 -P 3309 -uroot -proot \
  -e "SHOW VARIABLES LIKE 'log_replica_updates'"
```

Esperado: `ON`.

## Observar eventos CDC

```bash
docker compose logs -f cdc-sink
```

## Generar cambios

Desde otra terminal, contra el primario en puerto **3308**:

```bash
mysql -h 127.0.0.1 -P 3308 -uroot -proot inventory <<'SQL'
INSERT INTO customers (first_name, last_name, email) VALUES ('Linus', 'Torvalds', 'linus@example.com');
UPDATE customers SET email='linus@kernel.org' WHERE last_name='Torvalds';
DELETE FROM customers WHERE last_name='Torvalds';
INSERT INTO audit_log (message) VALUES ('NO debe aparecer en cdc-sink');
SQL
```

O con el generador automatizado:

```bash
cd ../load-generator
make venv          # primera vez
make run-8         # presiona C para parar
```

## Limpieza

```bash
docker compose down -v
```

## Troubleshooting

### `Replica_IO_Running: No` con error de auth
MySQL 8.0 puede negociar `caching_sha2_password` por defecto. Verifica que el usuario `repl` exista con `mysql_native_password`:
```bash
mysql -h 127.0.0.1 -P 3308 -uroot -proot \
  -e "SELECT user, plugin FROM mysql.user WHERE user='repl'"
```

### Debezium no se conecta al replica
El usuario `debezium` se crea en el primario y se replica. Confirma que llegó a la réplica:
```bash
mysql -h 127.0.0.1 -P 3309 -uroot -proot \
  -e "SELECT user, plugin FROM mysql.user WHERE user='debezium'"
```

### `Image quay.io/debezium/server:3.5.0.Final not found`
Confirma conectividad a quay.io: `docker pull quay.io/debezium/server:3.5.0.Final`. El repo de Docker Hub `debezium/server` NO contiene tags 3.x recientes — usa siempre quay.io.
