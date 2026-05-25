## 1. Estructura de archivos del escenario

- [x] 1.1 Crear el árbol de directorios bajo `withReplica/`: `mysql/primary/init/`, `mysql/replica/init/`, `debezium/conf/`
- [x] 1.2 Añadir `withReplica/.gitignore` para excluir cualquier dato local persistente generado por contenedores

## 2. Configuración de MySQL primario

- [x] 2.1 Crear `mysql/primary/my.cnf` con `server-id=1`, `log_bin=mysql-bin`, `binlog_format=ROW`, `binlog_row_image=FULL`, `gtid_mode=ON`, `enforce_gtid_consistency=ON`
- [x] 2.2 Crear `mysql/primary/init/01-users.sql` que cree el usuario de replicación (`repl@'%'` con `REPLICATION SLAVE`) y el usuario para Debezium (`debezium@'%'` con `REPLICATION SLAVE, REPLICATION CLIENT, SELECT, RELOAD` sobre `*.*`)
- [x] 2.3 Crear `mysql/primary/init/02-demo-schema.sql` que cree la base `inventory` con: (a) tabla `customers` con 2-3 filas seed (incluida en `table.include.list`), (b) tabla `audit_log` con 1 fila seed (NO incluida, sirve como control negativo del filtrado)

## 3. Configuración de MySQL replica

- [x] 3.1 Crear `mysql/replica/my.cnf` con `server-id=2`, `log_bin=mysql-bin`, `binlog_format=ROW`, `binlog_row_image=FULL`, `log_slave_updates=ON`, `gtid_mode=ON`, `enforce_gtid_consistency=ON`, `read_only=ON`
- [x] 3.2 Crear `mysql/replica/init/01-start-replica.sql` que ejecute `CHANGE MASTER TO MASTER_HOST='mysql-primary', MASTER_USER='repl', MASTER_PASSWORD='repl', MASTER_AUTO_POSITION=1` seguido de `START SLAVE` (sintaxis MySQL 5.7)
- [x] 3.3 Crear el usuario `debezium@'%'` también en la réplica con los mismos privilegios (necesario porque Debezium se conecta aquí)

## 4. Configuración de Debezium Server

- [x] 4.1 Crear `debezium/conf/application.properties` con:
  - `debezium.sink.type=http` (Debezium 2.4.x no incluye sink `log`; ese sink llegó en versiones que ya no soportan MySQL 5.7)
  - `debezium.sink.http.url=http://cdc-sink:8080`
  - `debezium.source.connector.class=io.debezium.connector.mysql.MySqlConnector`
  - `debezium.source.database.hostname=mysql-replica`
  - `debezium.source.database.port=3306`
  - `debezium.source.database.user=debezium`
  - `debezium.source.database.password=dbz`
  - `debezium.source.database.server.id=42`
  - `debezium.source.topic.prefix=replica-cdc`
  - `debezium.source.database.include.list=inventory`
  - `debezium.source.table.include.list=inventory.customers` (lista explícita de tablas de interés; añadir más separadas por coma, p.ej. `inventory.customers,inventory.orders`)
  - `debezium.source.schema.history.internal=io.debezium.storage.file.history.FileSchemaHistory`
  - `debezium.source.schema.history.internal.file.filename=/debezium/data/schema-history.dat`
  - `debezium.source.offset.storage.file.filename=/debezium/data/offsets.dat`
  - `debezium.source.snapshot.mode=initial`
- [x] 4.2 Documentar en un comentario del archivo cómo cambiar a `snapshot.mode=schema_only` para evitar el lock en la réplica
- [x] 4.3 Documentar en un comentario del archivo cómo invertir el filtro usando `table.exclude.list` (mutuamente excluyente con `table.include.list`) y cómo extender la inclusión a varias tablas con regex

## 5. docker-compose.yml

- [x] 5.1 Definir servicio `mysql-primary` (imagen `mysql:5.7`) con: variables `MYSQL_ROOT_PASSWORD=root`, montaje de `./mysql/primary/my.cnf` en `/etc/mysql/conf.d/my.cnf`, montaje de `./mysql/primary/init` en `/docker-entrypoint-initdb.d`, puerto host `3306:3306`, healthcheck con `mysqladmin ping`
- [x] 5.2 Definir servicio `mysql-replica` (imagen `mysql:5.7`) con: variables análogas, montajes de `my.cnf` e `init`, puerto host `3307:3306`, `depends_on: mysql-primary` con `condition: service_healthy`, healthcheck que verifique `Slave_IO_Running=Yes` y `Slave_SQL_Running=Yes`
- [x] 5.3 Definir servicio `debezium-server` (imagen `debezium/server:2.4.2.Final` — última versión oficialmente compatible con MySQL 5.7 según la matriz de releases de Debezium; 2.5+ desupported MySQL 5.7) con: montaje de `./debezium/conf` en `/debezium/conf`, volumen `debezium-data` en `/debezium/data` para offsets/schema history, `depends_on: mysql-replica` con `condition: service_healthy` y `cdc-sink` con `condition: service_started`
- [x] 5.4 Definir una red `bridge` interna compartida por todos los servicios
- [x] 5.5 (Opcional según D7) Añadir servicio `mysql-client` para correr comandos `mysql` ad-hoc vía `docker compose run --rm mysql-client ...`
- [x] 5.6 Definir servicio `cdc-sink` (imagen `mendhak/http-https-echo:40`) que recibe los POST de Debezium y los imprime en stdout — su contenedor de logs es la "consola" donde se ven los eventos CDC

## 6. Documentación

- [x] 6.1 Crear `withReplica/README.md` con secciones:
  - Descripción del escenario y diagrama de la topología (primary → replica → Debezium → consola)
  - Pre-requisitos (Docker + Docker Compose)
  - Comando de arranque: `docker compose up -d`
  - Cómo verificar replicación: ejemplo de `SHOW SLAVE STATUS\G` contra el puerto 3307
  - Cómo generar eventos: snippet con `INSERT/UPDATE/DELETE` contra el primario en puerto 3306
  - Cómo observar los eventos: `docker compose logs -f debezium-server`
  - Cómo limpiar: `docker compose down -v`
  - Sección de troubleshooting (réplica no arranca, Debezium no se conecta, no se ven eventos por falta de `log_slave_updates`)
  - Cómo cambiar puertos o credenciales

## 7. Verificación manual end-to-end

- [x] 7.1 Ejecutar `docker compose up -d` desde cero y confirmar que los tres servicios alcanzan `healthy`/`running`
- [x] 7.2 Conectarse a la réplica y validar que `SHOW SLAVE STATUS\G` reporta `Slave_IO_Running=Yes` y `Slave_SQL_Running=Yes`
- [x] 7.3 Validar que `SHOW VARIABLES LIKE 'log_slave_updates'` en la réplica devuelve `ON`
- [x] 7.4 Ejecutar un INSERT contra el primario y verificar que aparece un evento `op=c` en `docker compose logs cdc-sink`
- [x] 7.5 Repetir con UPDATE (esperar `op=u` con `before`/`after`) y DELETE (esperar `op=d` con `before`)
- [x] 7.6 Validar el filtrado: insertar una fila en `inventory.audit_log` (NO incluida) y confirmar que NO aparece evento alguno en los logs de `cdc-sink`
- [x] 7.7 Confirmar que `docker compose down -v` limpia todo y un nuevo `up -d` reproduce el mismo comportamiento

## 8. Generador de carga sintética (Python 3.12)

- [x] 8.1 Crear `load-generator/random_changes.py` que: (a) se conecta a `127.0.0.1:3306` con `PyMySQL`, (b) cada 10s ejecuta una operación aleatoria entre INSERT/UPDATE/DELETE sobre `inventory.customers`, (c) detiene al pulsar `C` (vía `termios.cbreak`) o al recibir SIGINT/SIGTERM
- [x] 8.2 Crear `load-generator/requirements.txt` con `PyMySQL==1.1.1`
- [x] 8.3 Crear `load-generator/Makefile` con targets `venv` (crea `.venv` con `python3.12` e instala `requirements.txt`), `venv-clean` (`rm -rf .venv`), y `run` (ejecuta el generador)
- [x] 8.4 Verificación: `make venv` construye el entorno; ejecución del generador produce eventos `op=c/u/d` visibles en `docker compose logs -f cdc-sink`

## 9. Reorganizar lo existente bajo `mysql5.7/`

- [x] 9.1 Tirar el stack actual con `docker compose down -v` (desde `withReplica/`) antes de mover archivos
- [x] 9.2 Crear directorio `withReplica/mysql5.7/` y mover `docker-compose.yml`, `mysql/`, `debezium/` dentro
- [x] 9.3 Mover `withReplica/README.md` original a `withReplica/mysql5.7/README.md` (queda como guía específica del stack 5.7)
- [x] 9.4 Crear nuevo `withReplica/README.md` top-level con resumen de los dos stacks y enlaces a los READMEs específicos
- [x] 9.5 Validar que `docker compose -f mysql5.7/docker-compose.yml config` sigue parseando sin errores
- [x] 9.6 Validar end-to-end: `cd mysql5.7 && docker compose up -d` y reproducir los scenarios 7.1–7.7 desde la nueva ubicación

## 10. Crear stack `mysql8/`

- [x] 10.1 Crear directorio `withReplica/mysql8/` con la misma estructura interna que `mysql5.7/` (`mysql/{primary,replica}/init`, `debezium/conf`)
- [x] 10.2 Crear `mysql8/mysql/primary/my.cnf` con `server-id=1`, `log_bin=mysql-bin`, `binlog_format=ROW`, `binlog_row_image=FULL`, `gtid_mode=ON`, `enforce_gtid_consistency=ON`
- [x] 10.3 Crear `mysql8/mysql/primary/init/01-users.sql` con `CREATE USER ... IDENTIFIED WITH mysql_native_password BY ...` para `repl` y `debezium`
- [x] 10.4 Crear `mysql8/mysql/primary/init/02-demo-schema.sql` (db `inventory`, tablas `customers` y `audit_log` con seed)
- [x] 10.5 Crear `mysql8/mysql/replica/my.cnf` con `log_replica_updates=ON`
- [x] 10.6 Crear `mysql8/mysql/replica/init/01-start-replica.sql` con `CHANGE REPLICATION SOURCE TO ... SOURCE_AUTO_POSITION=1, GET_SOURCE_PUBLIC_KEY=1` + `START REPLICA`. NO pre-crear el usuario `debezium`
- [x] 10.7 Crear `mysql8/mysql/replica/healthcheck.sh` validando `Replica_IO_Running: Yes` y `Replica_SQL_Running: Yes`
- [x] 10.8 Crear `mysql8/debezium/conf/application.properties` con sink `http`, conector MySQL apuntando a `mysql-replica:3306`, `database.include.list=inventory`, `table.include.list=inventory.customers`, `topic.prefix=replica-cdc-8`, `database.server.id=43`
- [x] 10.9 Crear `mysql8/debezium/Dockerfile` para construir imagen derivada de `quay.io/debezium/server:3.5.0.Final` que incluye el conector MySQL (descubrimiento durante la implementación: la imagen oficial 3.x solo trae preempaquetados los conectores de Cassandra; hay que descargar el connector plugin desde Maven Central y dejarlo en `/debezium/connectors/debezium-connector-mysql/` con un `extra_class_path.sh`)
- [x] 10.10 Crear `mysql8/docker-compose.yml` con cinco servicios: `mysql-primary` (host 3308), `mysql-replica` (host 3309), `debezium-server` (build local), `cdc-sink` (mendhak/http-https-echo:40), `mysql-client` (profile `tools`). Mount del config en `/debezium/config/` (cambió desde `/debezium/conf/` en 3.x).
- [x] 10.11 Crear `mysql8/README.md` documentando puertos 3308/3309, sintaxis moderna, troubleshooting

## 11. Refactorizar load-generator para soportar dos targets

- [x] 11.1 Modificar `load-generator/random_changes.py` con `argparse` + flag `--target {mysql5.7,mysql8}` (mapeo: 5.7→3306, 8→3308) y escape hatch `--host`/`--port`
- [x] 11.2 Actualizar `load-generator/Makefile`: eliminar `run` ambiguo y añadir `run-5.7` y `run-8`
- [x] 11.3 Añadir `cryptography` a `requirements.txt` (necesario porque `root` en MySQL 8.0 usa `caching_sha2_password` por defecto y PyMySQL lo requiere para esa auth)
- [x] 11.4 Verificar: `make run-5.7` produce eventos en `cdc-sink` del stack 5.7; `make run-8` los produce en el stack 8

## 12. Verificación end-to-end del stack mysql8

- [x] 12.1 `cd mysql8 && docker compose up -d` y confirmar que los cuatro servicios alcanzan `healthy`/`running`
- [x] 12.2 `SHOW REPLICA STATUS\G` contra `mysql-replica` del stack 8 reporta `Replica_IO_Running=Yes` y `Replica_SQL_Running=Yes`
- [x] 12.3 `SHOW VARIABLES LIKE 'log_replica_updates'` en la réplica del stack 8 devuelve `ON`
- [x] 12.4 INSERT/UPDATE/DELETE contra el primario del stack 8 producen eventos `op=c/u/d` en `docker compose logs cdc-sink` (de ese stack)
- [x] 12.5 INSERT en `inventory.audit_log` del stack 8 NO produce evento (filtrado por `table.include.list` también funciona en mysql8)
- [x] 12.6 Levantar **ambos stacks simultáneamente** y verificar que no hay conflicto de puertos ni de container names (verificado: 8 contenedores healthy en paralelo, puertos 3306/3307/3308/3309 disjuntos)
- [x] 12.7 `make run-5.7` solo afecta al stack 5.7; `make run-8` solo afecta al stack 8 — cross-check de aislamiento confirmado (3 eventos al stack target, 0 al otro)
