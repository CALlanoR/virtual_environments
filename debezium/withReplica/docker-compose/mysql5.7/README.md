# Debezium Server + MySQL primary/replica

Escenario local para experimentar con **Debezium Server consumiendo binlogs de una RÉPLICA MySQL** (no del primario), con eventos CDC impresos por consola.

## Topología

```
┌──────────────┐  replicación   ┌──────────────┐  binlog   ┌──────────────────┐  HTTP POST   ┌──────────┐
│ mysql-primary│ ─────────────▶│ mysql-replica│ ─────────▶│ debezium-server  │ ───────────▶│ cdc-sink │
│  :3306 host  │   (GTID, ROW) │  :3307 host  │  (lee aquí)│   (sink http)    │  evento JSON │ (stdout) │
└──────────────┘                └──────────────┘            └──────────────────┘              └──────────┘
       ▲ escrituras                  read_only=ON                                                docker compose
       │                              log_slave_updates=ON                                       logs -f cdc-sink
   tu cliente
```

- Las **escrituras** se hacen contra `mysql-primary` (puerto host **3306**).
- La **réplica** (`mysql-replica`, puerto host **3307**) tiene `log_slave_updates=ON`, así que reescribe los cambios replicados en su propio binlog.
- **Debezium Server** (`2.4.2.Final`, última versión que soporta MySQL 5.7) se conecta a `mysql-replica:3306` y, vía sink `http`, hace POST de cada evento al servicio `cdc-sink`.
- **`cdc-sink`** es un contenedor `mendhak/http-https-echo` que imprime cada request entrante en su stdout. Allí ves los eventos CDC.

## Pre-requisitos

- Docker Engine 20.10+ y Docker Compose v2 (`docker compose ...`).
- Cliente `mysql` local (opcional; si no lo tienes, usa el servicio `mysql-client` incluido).
- Puertos host **3306** y **3307** libres.

## Levantar el stack

```bash
docker compose up -d
```

El arranque es secuencial gracias a healthchecks:
1. `mysql-primary` se inicializa, ejecuta los scripts de `mysql/primary/init/` (crea usuarios `repl` y `debezium`, base `inventory` con tablas `customers` y `audit_log`).
2. `mysql-replica` arranca cuando primary está `healthy`, ejecuta `CHANGE MASTER TO ... + START SLAVE`. Su healthcheck valida `Slave_IO_Running=Yes` y `Slave_SQL_Running=Yes`.
3. `debezium-server` arranca cuando la réplica está `healthy`, hace el snapshot inicial de `inventory.customers` y luego entra en streaming.

Verifica el estado:

```bash
docker compose ps
```

## Verificar la replicación primary→replica

Con cliente `mysql` local:

```bash
mysql -h 127.0.0.1 -P 3307 -uroot -proot -e 'SHOW SLAVE STATUS\G' | grep -E 'Slave_(IO|SQL)_Running|Last_Error'
```

O sin cliente local:

```bash
docker compose run --rm mysql-client \
  mysql -hmysql-replica -uroot -proot -e 'SHOW SLAVE STATUS\G'
```

Debes ver `Slave_IO_Running: Yes` y `Slave_SQL_Running: Yes`.

Validar también que `log_slave_updates` está activo en la réplica:

```bash
mysql -h 127.0.0.1 -P 3307 -uroot -proot -e "SHOW VARIABLES LIKE 'log_slave_updates'"
```

## Observar los eventos CDC

En una terminal aparte:

```bash
docker compose logs -f cdc-sink
```

Cada cambio aparecerá como un POST a `/`, con el evento CDC en el cuerpo JSON. Algo así:

```
{
  "method": "POST",
  "path": "/",
  "body": "{\"schema\":...,\"payload\":{\"before\":null,\"after\":{\"id\":4,\"first_name\":\"Linus\",...},\"op\":\"c\",...}}"
}
```

Para ver los logs de Debezium (snapshot, streaming, errores) usa `docker compose logs -f debezium-server`.

## Generar cambios

Conéctate al **primario** y ejecuta SQL contra `inventory.customers` (incluida) y `inventory.audit_log` (NO incluida):

```bash
mysql -h 127.0.0.1 -P 3306 -uroot -proot inventory
```

```sql
-- Genera evento op=c en debezium-server
INSERT INTO customers (first_name, last_name, email)
VALUES ('Linus', 'Torvalds', 'linus@example.com');

-- Genera evento op=u
UPDATE customers SET email = 'linus@kernel.org' WHERE last_name = 'Torvalds';

-- Genera evento op=d
DELETE FROM customers WHERE last_name = 'Torvalds';

-- NO debe generar evento (audit_log NO está en table.include.list)
INSERT INTO audit_log (message) VALUES ('this should NOT show in debezium logs');
```

## Limpieza

```bash
docker compose down -v
```

`-v` borra el volumen `debezium-data` (offsets y schema history). Sin él, si vuelves a levantar el stack, Debezium reanudará desde el último offset.

## Cambiar puertos / credenciales

| Qué | Dónde |
| --- | --- |
| Puerto host del primario | `docker-compose.yml`, servicio `mysql-primary`, sección `ports` (`"3306:3306"`) |
| Puerto host de la réplica | `docker-compose.yml`, servicio `mysql-replica`, sección `ports` (`"3307:3306"`) |
| Password de root | `MYSQL_ROOT_PASSWORD` en ambos servicios MySQL (recuerda actualizarlo también en el healthcheck script `mysql/replica/healthcheck.sh` y en los `init/*.sql` si dependen de root) |
| Usuario/contraseña de Debezium | `mysql/primary/init/01-users.sql`, `mysql/replica/init/01-start-replica.sql`, y `debezium/conf/application.properties` (`debezium.source.database.user/password`) |
| Usuario/contraseña de replicación | `mysql/primary/init/01-users.sql` y `mysql/replica/init/01-start-replica.sql` (`MASTER_USER`, `MASTER_PASSWORD`) |

## Cambiar las tablas observadas por Debezium

En `debezium/conf/application.properties`:

```properties
# Whitelist explícita (recomendado para demos):
debezium.source.table.include.list=inventory.customers,inventory.orders

# O con regex:
debezium.source.table.include.list=inventory\\.(customers|orders)

# O blacklist (mutuamente excluyente con table.include.list):
#debezium.source.table.exclude.list=inventory.audit_log
```

Después de cambiar el filtro, reinicia Debezium **borrando el schema history** (porque el set de tablas observadas cambió):

```bash
docker compose stop debezium-server
docker volume rm withreplica_debezium-data
docker compose up -d debezium-server
```

## Troubleshooting

### La réplica no arranca / `Slave_IO_Running: No`
- Comprueba los logs: `docker compose logs mysql-replica`.
- Causa típica: el primario no estaba listo cuando la réplica corrió `CHANGE MASTER TO`. El `depends_on: condition: service_healthy` debería evitarlo, pero si pasa: `docker compose down -v && docker compose up -d`.
- Otra causa: `repl@'%'` no existe en el primario. Revisa que `mysql/primary/init/01-users.sql` se haya ejecutado.

### Debezium no se conecta a la réplica
- `docker compose logs debezium-server` debería mostrar el error exacto.
- Verifica que el usuario `debezium` existe en la réplica: `docker compose run --rm mysql-client mysql -hmysql-replica -uroot -proot -e "SELECT user FROM mysql.user WHERE user='debezium'"`.
- Verifica que `debezium.source.database.hostname` apunta a `mysql-replica` (no a `mysql-primary`).

### No veo eventos en los logs aunque inserto en el primario
La causa #1 de este patrón es que la réplica no tiene `log_slave_updates=ON` y, por tanto, no reescribe los cambios en su propio binlog. Verifica:

```bash
mysql -h 127.0.0.1 -P 3307 -uroot -proot -e "SHOW VARIABLES LIKE 'log_slave_updates'"
```

Debe devolver `ON`. Si está en `OFF`, revisa `mysql/replica/my.cnf` y reinicia el stack con `docker compose down -v && docker compose up -d`.

### Veo eventos de tablas que no me interesan
Estás viendo todas las tablas porque `table.include.list` está mal o falta. Revisa `debezium/conf/application.properties`. Recuerda borrar el volumen `debezium-data` al cambiar el filtro (ver "Cambiar las tablas observadas").

### `No Debezium consumer named 'log' is available`
El sink `log` no existe en Debezium Server 2.4.x; se añadió en versiones posteriores que ya no soportan MySQL 5.7. En este escenario usamos sink `http` con el sidecar `cdc-sink`. Si lo cambiaste a `log`, vuelve a `debezium.sink.type=http` y `debezium.sink.http.url=http://cdc-sink:8080` en `debezium/conf/application.properties`.

### Quiero forzar un re-snapshot
```bash
docker compose stop debezium-server
docker volume rm withreplica_debezium-data
docker compose up -d debezium-server
```

## Estructura de archivos

```
withReplica/
├── docker-compose.yml             # 4 servicios: mysql-primary, mysql-replica, debezium-server, cdc-sink (+ mysql-client opcional)
├── README.md
├── .gitignore
├── mysql/
│   ├── primary/
│   │   ├── my.cnf
│   │   └── init/
│   │       ├── 01-users.sql        # crea usuarios repl y debezium
│   │       └── 02-demo-schema.sql  # crea inventory.customers + inventory.audit_log
│   └── replica/
│       ├── my.cnf
│       ├── healthcheck.sh          # valida que la replicación está corriendo
│       └── init/
│           └── 01-start-replica.sql  # solo CHANGE MASTER TO + START SLAVE; los usuarios llegan replicados
└── debezium/
    └── conf/
        └── application.properties  # sink=http apuntando a cdc-sink:8080
```
