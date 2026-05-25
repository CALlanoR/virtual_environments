## ADDED Requirements

### Requirement: Stack reproducible vía docker-compose
El sistema SHALL proveer un único archivo `docker-compose.yml` en `withReplica/` que orqueste tres servicios — `mysql-primary`, `mysql-replica` y `debezium-server` — y que permita arrancar todo el escenario con un único comando `docker compose up`.

#### Scenario: Arranque limpio del stack
- **WHEN** el usuario ejecuta `docker compose up -d` desde el directorio `withReplica/` con un Docker daemon funcional
- **THEN** los tres servicios alcanzan estado `healthy` (o `running` para Debezium) sin requerir intervención manual adicional

#### Scenario: Apagado y limpieza
- **WHEN** el usuario ejecuta `docker compose down -v` desde `withReplica/`
- **THEN** todos los contenedores y volúmenes anónimos creados por el stack son eliminados y el siguiente `docker compose up` parte de un estado limpio

### Requirement: Replicación primary-to-replica activa
El sistema SHALL configurar `mysql-primary` como source y `mysql-replica` como replica, de tal forma que tras el arranque la réplica esté replicando activamente desde el primario usando GTID y formato `ROW`.

#### Scenario: Verificar estado de replicación
- **WHEN** se ejecuta `SHOW SLAVE STATUS\G` contra `mysql-replica` después de que el stack esté `healthy`
- **THEN** los campos `Slave_IO_Running` y `Slave_SQL_Running` reportan `Yes` y `Last_Error` está vacío

#### Scenario: Cambios aplicados en primary se ven en replica
- **WHEN** el usuario inserta una fila en una tabla del primario y espera unos segundos
- **THEN** la misma fila es consultable desde la réplica con los mismos valores

### Requirement: Replica reescribe cambios en su propio binlog
El sistema SHALL configurar la réplica con `log_slave_updates=ON`, `binlog_format=ROW` y `binlog_row_image=FULL`, de modo que los cambios replicados desde el primario queden registrados en el binlog local de la réplica y sean consumibles por Debezium.

#### Scenario: log_slave_updates activo
- **WHEN** se consulta `SHOW VARIABLES LIKE 'log_slave_updates'` contra la réplica
- **THEN** el valor reportado es `ON`

#### Scenario: Binlogs de la replica contienen cambios replicados
- **WHEN** se ejecuta un INSERT en el primario y luego `SHOW BINLOG EVENTS` contra la réplica
- **THEN** el evento correspondiente aparece en el binlog de la réplica

### Requirement: Debezium Server se conecta a la replica
El sistema SHALL configurar `debezium-server` para conectarse al hostname `mysql-replica` (no al primario) usando un usuario dedicado con los privilegios `REPLICATION SLAVE`, `REPLICATION CLIENT`, `SELECT` y `RELOAD`.

#### Scenario: Configuración apunta a la replica
- **WHEN** se inspecciona `debezium/conf/application.properties`
- **THEN** la propiedad `debezium.source.database.hostname` es `mysql-replica` y `debezium.source.database.user` es un usuario distinto de `root`

#### Scenario: Debezium completa el snapshot inicial
- **WHEN** Debezium arranca contra una réplica recién inicializada
- **THEN** los logs del contenedor `debezium-server` muestran un mensaje indicando snapshot completado y transición a streaming de binlog

### Requirement: Filtrado por lista explícita de tablas
El sistema SHALL configurar Debezium Server con `debezium.source.table.include.list` apuntando a una lista explícita y no vacía de tablas totalmente cualificadas (`db.tabla`), de modo que solo los cambios de esas tablas se emitan al sink. Tablas fuera de la lista NO SHALL producir eventos.

#### Scenario: La configuración declara una lista de tablas
- **WHEN** se inspecciona `debezium/conf/application.properties`
- **THEN** la propiedad `debezium.source.table.include.list` está presente, no vacía, y cada entrada tiene la forma `db.tabla`

#### Scenario: Cambio en una tabla incluida produce evento
- **WHEN** el usuario inserta una fila en una tabla que aparece en `table.include.list`
- **THEN** los logs de `cdc-sink` muestran un evento CDC para esa fila

#### Scenario: Cambio en una tabla no incluida es ignorado
- **WHEN** existe en la base de demo una tabla que NO aparece en `table.include.list` y el usuario inserta una fila en ella
- **THEN** los logs de `cdc-sink` NO muestran ningún evento CDC para esa fila

### Requirement: Eventos CDC visibles por consola
El sistema SHALL configurar Debezium Server con un sink que entrega cada evento CDC a un servicio cuyo stdout sea observable vía `docker compose logs`. En esta implementación se usa `debezium.sink.type=http` apuntando a un sidecar `cdc-sink` (imagen `mendhak/http-https-echo`) que imprime cada request entrante.

#### Scenario: INSERT genera evento observable
- **WHEN** el usuario inserta una fila en una tabla incluida en `table.include.list` del primario
- **THEN** los logs de `cdc-sink` muestran un POST con un evento que contiene `op=c` (create) y la fila insertada en `after`

#### Scenario: UPDATE genera evento observable
- **WHEN** el usuario actualiza una fila existente en el primario
- **THEN** los logs de `cdc-sink` muestran un POST con un evento que contiene `op=u` (update) con `before` y `after`

#### Scenario: DELETE genera evento observable
- **WHEN** el usuario elimina una fila existente en el primario
- **THEN** los logs de `cdc-sink` muestran un POST con un evento que contiene `op=d` (delete) con la fila eliminada en `before`

### Requirement: Datos de demostración pre-cargados
El sistema SHALL crear automáticamente, durante el bootstrap del primario, una base de datos de demo, al menos una tabla **incluida** en `table.include.list` con filas seed, y al menos una tabla **no incluida** (control negativo) que permita validar el filtrado.

#### Scenario: Esquema demo disponible tras el arranque
- **WHEN** el stack alcanza estado `healthy`
- **THEN** existe en `mysql-primary` una base de datos de demo (por ejemplo `inventory`) con al menos una tabla incluida en `table.include.list` y otra tabla NO incluida, ambas con filas seed

#### Scenario: Esquema demo replicado en la replica
- **WHEN** se consulta la base de datos de demo contra `mysql-replica` tras el arranque
- **THEN** la base de datos y sus tablas existen con las mismas filas que en el primario

### Requirement: Generador de carga sintética en Python con selector de target
El sistema SHALL incluir, bajo `withReplica/load-generator/`, un programa Python 3.12 que se conecte al primario del stack indicado por el flag `--target {mysql5.7,mysql8}` y ejecute operaciones aleatorias sobre `inventory.customers` (`INSERT`, `UPDATE` o `DELETE` elegidas al azar) cada 10 segundos hasta que el usuario lo detenga. El programa SHALL mapear `mysql5.7` al puerto 3306 y `mysql8` al puerto 3308 por defecto, con flags opcionales `--host`/`--port` para sobrescribir.

#### Scenario: Selección de target mysql5.7
- **WHEN** se ejecuta `random_changes.py --target mysql5.7` con el stack 5.7 corriendo
- **THEN** las operaciones llegan al primario del stack 5.7 (puerto 3306) y los eventos CDC aparecen en los logs de `cdc-sink` de ese stack

#### Scenario: Selección de target mysql8
- **WHEN** se ejecuta `random_changes.py --target mysql8` con el stack 8 corriendo
- **THEN** las operaciones llegan al primario del stack 8 (puerto 3308) y los eventos CDC aparecen en los logs de `cdc-sink` de ese stack

#### Scenario: Target requerido
- **WHEN** se ejecuta `random_changes.py` sin `--target` ni `--host/--port`
- **THEN** el programa rechaza la ejecución con un mensaje de error indicando que falta el target

#### Scenario: Periodicidad y aleatoriedad
- **WHEN** el generador se ejecuta de forma continua durante al menos 30 segundos contra un primario operativo
- **THEN** ha emitido al menos 3 sentencias SQL contra `inventory.customers`, cada una elegida aleatoriamente entre `INSERT`, `UPDATE` y `DELETE`, separadas aproximadamente por 10 segundos

#### Scenario: Detención con la tecla C
- **WHEN** el usuario pulsa la tecla `C` (o `c`) mientras el generador corre con stdin conectado a un TTY
- **THEN** el generador detiene el bucle, cierra la conexión a MySQL y termina con exit code 0

#### Scenario: Detención con SIGINT
- **WHEN** el usuario envía `Ctrl+C` (SIGINT) o el script recibe SIGTERM
- **THEN** el generador detiene el bucle, cierra la conexión a MySQL y termina con exit code 0

#### Scenario: Operaciones disparan eventos CDC
- **WHEN** el generador inserta/actualiza/elimina filas en `inventory.customers` con el stack en marcha
- **THEN** los eventos correspondientes (`op=c`, `op=u`, `op=d`) aparecen en los logs de `cdc-sink`

### Requirement: Makefile para gestionar el venv del generador
El sistema SHALL incluir un `Makefile` en `withReplica/load-generator/` con un target que cree un entorno virtual usando Python 3.12 e instale las dependencias, otro que lo elimine, y targets `run-5.7` y `run-8` que ejecuten el generador apuntando al stack correspondiente.

#### Scenario: Crear el venv
- **WHEN** se ejecuta `make venv` desde `withReplica/load-generator/` con `python3.12` disponible en el PATH
- **THEN** se crea el directorio `.venv/` con un intérprete Python 3.12 y `PyMySQL` instalado, sin requerir más comandos manuales

#### Scenario: Eliminar el venv
- **WHEN** se ejecuta `make venv-clean` desde `withReplica/load-generator/`
- **THEN** el directorio `.venv/` se elimina por completo (idempotente: no falla si ya no existe)

#### Scenario: Target run-5.7
- **WHEN** se ejecuta `make run-5.7`
- **THEN** se invoca `random_changes.py --target mysql5.7` con el intérprete del venv

#### Scenario: Target run-8
- **WHEN** se ejecuta `make run-8`
- **THEN** se invoca `random_changes.py --target mysql8` con el intérprete del venv

### Requirement: Documentación de uso
El sistema SHALL incluir un `README.md` en `withReplica/` que documente cómo arrancar el stack, generar cambios de prueba, observar los eventos en los logs de Debezium y limpiar el entorno.

#### Scenario: README incluye los comandos esenciales
- **WHEN** un nuevo usuario abre `withReplica/README.md`
- **THEN** encuentra al menos: comando para `docker compose up`, comando para conectarse al primario y ejecutar SQL de prueba, comando para seguir los logs de Debezium, y comando para tear-down

### Requirement: Estructura de dos stacks paralelos
El sistema SHALL organizar el escenario en dos subdirectorios `withReplica/mysql5.7/` y `withReplica/mysql8/`, cada uno autocontenido (su propio `docker-compose.yml`, configs MySQL, config Debezium), de modo que ambos puedan ejecutarse simultáneamente sin conflicto de puertos.

#### Scenario: Existencia de los dos stacks
- **WHEN** se inspecciona `withReplica/`
- **THEN** existen los subdirectorios `mysql5.7/` y `mysql8/`, cada uno conteniendo un `docker-compose.yml` válido

#### Scenario: Puertos host disjuntos
- **WHEN** se inspeccionan los `docker-compose.yml` de ambos stacks
- **THEN** los puertos host no se solapan: stack 5.7 publica 3306 (primary) y 3307 (replica); stack 8 publica 3308 (primary) y 3309 (replica)

#### Scenario: Ejecución simultánea de ambos stacks
- **WHEN** el usuario ejecuta `docker compose up -d` en ambos directorios consecutivamente
- **THEN** los ocho contenedores (cuatro por stack) alcanzan estado `healthy`/`running` sin colisiones

### Requirement: Stack mysql5.7 con sintaxis y versiones legacy
El sistema SHALL usar `mysql:5.7` y `debezium/server:2.4.2.Final` (Docker Hub) en el stack `mysql5.7/`, empleando la sintaxis de replicación clásica (`CHANGE MASTER TO`, `START SLAVE`, `SHOW SLAVE STATUS`, variable `log_slave_updates`).

#### Scenario: Versiones del stack 5.7
- **WHEN** se inspecciona `mysql5.7/docker-compose.yml`
- **THEN** los servicios MySQL declaran `image: mysql:5.7` y el servicio Debezium declara `image: debezium/server:2.4.2.Final`

#### Scenario: Sintaxis legacy en el init de la réplica 5.7
- **WHEN** se inspeccionan los scripts de inicialización de la réplica del stack 5.7
- **THEN** usan `CHANGE MASTER TO ... MASTER_AUTO_POSITION=1` y `START SLAVE`, no la sintaxis moderna

### Requirement: Stack mysql8 con sintaxis moderna y Debezium 3.5 desde quay.io
El sistema SHALL usar `mysql:8.0` y `quay.io/debezium/server:3.5.0.Final` en el stack `mysql8/`, empleando la sintaxis de replicación moderna (`CHANGE REPLICATION SOURCE TO`, `START REPLICA`, `SHOW REPLICA STATUS`, variable `log_replica_updates`). La imagen de Debezium DEBE provenir de `quay.io` porque el repo de Docker Hub `docker.io/debezium/server` no contiene tags 3.1+.

#### Scenario: Versiones del stack 8
- **WHEN** se inspecciona `mysql8/docker-compose.yml`
- **THEN** los servicios MySQL declaran `image: mysql:8.0` y el servicio Debezium declara `image: quay.io/debezium/server:3.5.0.Final`

#### Scenario: Sintaxis moderna en el init de la réplica 8
- **WHEN** se inspeccionan los scripts de inicialización de la réplica del stack 8
- **THEN** usan `CHANGE REPLICATION SOURCE TO ... SOURCE_AUTO_POSITION=1` y `START REPLICA`, y la variable `log_replica_updates` aparece en el `my.cnf` de la réplica

#### Scenario: Healthcheck del stack 8 usa los nombres modernos
- **WHEN** se inspecciona el healthcheck de `mysql-replica` del stack 8
- **THEN** verifica los campos `Replica_IO_Running` y `Replica_SQL_Running` (no los legacy `Slave_*`)
