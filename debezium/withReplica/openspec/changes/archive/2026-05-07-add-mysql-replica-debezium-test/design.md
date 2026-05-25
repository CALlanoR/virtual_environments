## Context

El directorio `withReplica/` está vacío y forma parte de un grupo de escenarios bajo `virtual_environments/debezium/`. Necesitamos un entorno reproducible que arranque con un solo `docker compose up` y que permita demostrar Debezium Server consumiendo binlogs desde una **réplica** MySQL (no desde el primario), para experimentar con el patrón "CDC desde la réplica" sin afectar la carga de un primario.

Los componentes involucrados son:
- MySQL primario que acepta escrituras y emite binlogs.
- MySQL réplica que se suscribe al primario y, gracias a `log_slave_updates=ON`, vuelve a escribir esos cambios en su propio binlog.
- Debezium Server (modo standalone, no Kafka Connect) que se conecta a la réplica con el conector MySQL y enruta los eventos a un sink.

## Goals / Non-Goals

**Goals:**
- **Dos stacks paralelos** (`mysql5.7/` y `mysql8/`), cada uno reproducible vía `docker compose up` desde su propio directorio.
- Replicación primary→replica funcional al arrancar en ambos stacks, sin pasos manuales más allá de los scripts de init.
- Debezium Server leyendo binlogs de la **réplica** (no del primario) en ambos stacks.
- Eventos CDC observables desde `docker compose logs -f cdc-sink` en ambos stacks.
- Documentación clara para generar INSERT/UPDATE/DELETE contra el stack elegido.
- Generador de carga compartido con selector `--target {mysql5.7,mysql8}`.
- Capacidad de ejecutar **ambos stacks simultáneamente** (puertos host disjuntos).

**Non-Goals:**
- Kafka, Kafka Connect, Schema Registry u otros sinks (Pulsar, Kinesis, etc.).
- Alta disponibilidad, GTID multi-source, failover, ni configuración para producción.
- Pruebas automatizadas (unit/integration) sobre los eventos generados; la verificación es manual vía logs.
- Soportar múltiples versiones de MySQL u opciones de PostgreSQL.
- Persistencia/volúmenes nombrados que sobrevivan a `docker compose down -v`; el escenario es efímero.

## Decisions

### D1: Versiones e imágenes (dos pares)

**Stack `mysql5.7/`:**
- `mysql:5.7` para primario y réplica. Sintaxis clásica: `CHANGE MASTER TO` / `START SLAVE` / `SHOW SLAVE STATUS`, variable `log_slave_updates`.
- **`debezium/server:2.4.2.Final`** (Docker Hub) — última versión de Debezium Server que oficialmente soporta MySQL 5.7. Matriz 2.4.x: "MySQL 5.7, 8.0.x"; a partir de **2.5.0.Beta1, MySQL 5.7 fue desupported** (*"MySQL 5.7 desupported; Support for MySQL 8.2"*).
  - Fuentes: <https://debezium.io/releases/2.4/>, <https://debezium.io/releases/2.5/>.

**Stack `mysql8/`:**
- `mysql:8.0` para primario y réplica. Sintaxis moderna (8.0.23+): `CHANGE REPLICATION SOURCE TO` / `START REPLICA` / `SHOW REPLICA STATUS`, variable `log_replica_updates`.
- **`quay.io/debezium/server:3.5.0.Final`** — última versión `.Final` estable de Debezium 3.x al 2026-05-07. Matriz 3.5: "MySQL 8.0.x, 8.4.x, 9.0, 9.1".
  - Fuente: <https://debezium.io/releases/3.5/>.

Alternativas consideradas:
- Versión `mysql:8.4` o `mysql:9.x` para el stack mysql8: las dos están en la matriz de Debezium 3.5, pero `mysql:8.0` es la versión 8 más extendida y la más estable. Si en el futuro queremos demostrar 8.4, basta con bumpear el tag.
- Mantener un único stack y parametrizar versiones con env vars: descartado, complica el `docker-compose.yml` y los scripts SQL (la sintaxis SQL distinta entre 5.7 y 8.0 no se acomoda bien con variables); dos archivos separados son más claros y diff-amigables.

**Nota de soporte**: MySQL 5.7 alcanzó EOL upstream en 2023 y Debezium 2.4 dejó de recibir patches al salir 2.5; aceptable para un escenario local de pruebas, no para producción. MySQL 8.0 + Debezium 3.5 sí está dentro de la matriz oficial.

### D2: Topología de replicación
- Replicación clásica binlog-based con `server-id` distinto por nodo.
- `log_slave_updates=ON` en la réplica para que sus binlogs reflejen los cambios replicados — **requisito** para que Debezium pueda consumirlos. (En MySQL 5.7 la variable se llama `log_slave_updates`; aún no existe el alias `log_replica_updates` de 8.0.26+.)
- `binlog_format=ROW` y `binlog_row_image=FULL` en ambos para que los eventos contengan before/after completos.
- GTID activado (`gtid_mode=ON`, `enforce_gtid_consistency=ON`) para simplificar el `CHANGE MASTER TO ... MASTER_AUTO_POSITION=1` en el script de init de la réplica. (MySQL 5.7 usa `CHANGE MASTER TO` / `START SLAVE`; la sintaxis `CHANGE REPLICATION SOURCE TO` / `START REPLICA` solo existe desde 8.0.23.)
- Alternativa considerada: replicación file/position. Descartada: el script de init tendría que leer el `SHOW MASTER STATUS` del primario en runtime, lo que complica el bootstrap declarativo.

### D3: Punto de origen para Debezium
- Debezium se conecta a `mysql-replica:3306` con un usuario dedicado (`debezium`) que tiene `REPLICATION SLAVE`, `REPLICATION CLIENT`, `SELECT`, `RELOAD`.
- En `application.properties`: `debezium.source.database.hostname=mysql-replica`.
- Se documenta que las **escrituras** se hacen contra `mysql-primary` (puerto host 3306) y que Debezium las observa porque la réplica las re-loguea en su propio binlog.

### D4: Sink hacia consola vía HTTP echo
- `debezium.sink.type=http` con `debezium.sink.http.url=http://cdc-sink:8080`.
- Servicio sidecar `cdc-sink` (imagen `mendhak/http-https-echo:40`) que imprime cada request entrante en su stdout. Eventos visibles con `docker compose logs -f cdc-sink`.
- **Por qué no `log` directamente en Debezium**: el sink `log` (`io.debezium.server.log.LogChangeConsumer`) **no existe en Debezium Server 2.4.x** — se añadió en versiones posteriores. Como 2.4.2.Final es la última versión que soporta oficialmente MySQL 5.7 (D1), no podemos combinar "sink log" + "MySQL 5.7 oficial". Los sinks que sí trae 2.4.2.Final son: `kafka`, `kinesis`, `pravega`, `pulsar`, `pubsub`, `eventhubs`, `redis`, `nats-*`, `http`, `rabbitmq`, `rocketmq`, `infinispan`.
- Alternativas consideradas:
  - Subir Debezium a 2.7.x para usar `log` directo: descartado, sale de la matriz oficial para MySQL 5.7.
  - Sink `kafka` con un consumer de consola: descartado, viola el Non-Goal "no Kafka".
  - Sink `pravega`/`pulsar`/`redis`: descartado, todos requieren broker adicional con más complejidad operativa que un simple http-echo.
  - Logging Quarkus en DEBUG (`quarkus.log.category."io.debezium".level=DEBUG`): descartado, mezcla los eventos con mucho ruido interno.
- Trade-off: añade un 4º contenedor y los eventos no salen del log del propio Debezium, pero conserva la matriz oficial Debezium↔MySQL y mantiene "ver eventos por consola" como flujo principal.

### D4b: Filtrado de tablas de interés
- Usar **`debezium.source.table.include.list`** (lista de tablas totalmente cualificadas `db.tabla`, separadas por coma) para capturar solo las tablas que nos interesan, sin tocar el resto de tablas que pueda existir en la base de demo.
- Mantener `debezium.source.database.include.list=inventory` como filtro de primer nivel; Debezium aplica primero el filtro de base y luego el de tabla.
- En el escenario de demo se incluye al menos `inventory.customers` (la tabla con datos seed). Se documenta cómo añadir más tablas o pasar a una lista negra con `table.exclude.list` (ambos son mutuamente excluyentes).
- Alternativas consideradas:
  - Solo `database.include.list` sin filtro de tabla. Descartada: capturaría toda la base, lo que dificulta razonar sobre qué eventos vienen de qué cambio durante una demo.
  - `table.exclude.list`. Descartada como default: en una demo el modelo "incluir lo que quiero ver" es más predecible que "excluir lo que no quiero".

### D5: Estructura de archivos
```
withReplica/
├── README.md                         # overview de los dos stacks + cómo elegir
├── mysql5.7/
│   ├── docker-compose.yml            # 4 servicios + mysql-client opcional, puertos 3306/3307
│   ├── mysql/{primary,replica}/...   # my.cnf + init scripts (sintaxis 5.7)
│   └── debezium/conf/application.properties
├── mysql8/
│   ├── docker-compose.yml            # 4 servicios + mysql-client opcional, puertos 3308/3309
│   ├── mysql/{primary,replica}/...   # my.cnf + init scripts (sintaxis 8.0)
│   └── debezium/conf/application.properties
└── load-generator/
    ├── Makefile                      # venv / venv-clean / run-5.7 / run-8
    ├── requirements.txt              # PyMySQL==1.1.1
    └── random_changes.py             # acepta --target {mysql5.7,mysql8}
```
Los archivos en `mysql/<role>/init/` se montan en `/docker-entrypoint-initdb.d/` y se ejecutan en orden alfabético.

**Nota**: el script de la réplica NO debe pre-crear el usuario `debezium`. Si lo hace, cuando la replicación reproduzca el `CREATE USER` del binlog del primario, el SQL thread fallará con error 1396. La solución correcta es dejar que la replicación propague el usuario desde `mysql.user` del primario. Esto aplica a ambos stacks.

**Nota**: el script `01-start-replica.sql` NO debe pre-crear el usuario `debezium`. Si lo hace, cuando la replicación reproduzca el `CREATE USER` que viene del binlog del primario, el SQL thread fallará con error 1396 ("Operation CREATE USER failed for 'debezium'@'%'") porque el `CREATE USER` replicado no incluye `IF NOT EXISTS`. La solución correcta es dejar que la replicación propague el usuario desde `mysql.user` del primario.

### D6: Orquestación y arranque
- `depends_on` con `condition: service_healthy` para que la réplica espere al primario y Debezium espere a la réplica.
- Debezium también `depends_on: cdc-sink` con `condition: service_started` (sin healthcheck, basta con que el contenedor esté arriba para aceptar el primer POST).
- Healthchecks por contenedor MySQL usando `mysqladmin ping -h localhost`.
- Healthcheck adicional/condicional para la réplica que verifique `Slave_IO_Running=Yes` y `Slave_SQL_Running=Yes` antes de marcar como healthy (script bash en el healthcheck).
- Alternativa considerada: orden por `depends_on` simple sin healthchecks. Descartada: Debezium fallaría al conectar antes de que la réplica termine su init.

### D8: Sintaxis MySQL — 5.7 vs 8.0

| Concepto | mysql5.7/ | mysql8/ |
|---|---|---|
| Apuntar al source | `CHANGE MASTER TO MASTER_HOST=...` | `CHANGE REPLICATION SOURCE TO SOURCE_HOST=...` |
| Iniciar replicación | `START SLAVE` | `START REPLICA` |
| Estado de replicación | `SHOW SLAVE STATUS\G` | `SHOW REPLICA STATUS\G` |
| Variable de re-logging | `log_slave_updates` | `log_replica_updates` (alias desde 8.0.26; el legacy también funciona pero usamos el moderno) |
| Campos de status | `Slave_IO_Running`, `Slave_SQL_Running` | `Replica_IO_Running`, `Replica_SQL_Running` |
| Auto-positioning | `MASTER_AUTO_POSITION=1` | `SOURCE_AUTO_POSITION=1` |

El script de healthcheck de la réplica del stack mysql8 es estructuralmente igual al de mysql5.7 pero hace grep contra `Replica_IO_Running` / `Replica_SQL_Running`.

### D9: Imágenes Debezium 3.x viven en quay.io, no en Docker Hub

**Hallazgo durante implementación**: el repo `docker.io/debezium/server` no se actualiza desde 2024-10-17 (último tag: `3.0.0.Final`). Las versiones 3.1+ se publican en **`quay.io/debezium/server`**. Verificado vía Docker Hub API y manifest inspect contra ambos registros.

Implicaciones:
- El stack `mysql8/docker-compose.yml` usa `image: quay.io/debezium/server:3.5.0.Final`.
- El stack `mysql5.7/docker-compose.yml` mantiene `image: debezium/server:2.4.2.Final` (Docker Hub) — esa versión sí existe allí.
- `docker compose pull` en el stack mysql8 hará pull de quay.io automáticamente; no requiere login si el repo es público.

### D10: Selector de target en el load generator

- `random_changes.py` acepta `--target {mysql5.7,mysql8}` (requerido). Internamente mapea:
  - `mysql5.7` → `127.0.0.1:3306`
  - `mysql8` → `127.0.0.1:3308`
- Argumentos opcionales `--host` y `--port` sirven como escape hatch (por ejemplo, si el usuario cambió los puertos en el compose).
- El `Makefile` añade `run-5.7` y `run-8`. El target `run` original puede mantenerse como alias del `run-5.7` o eliminarse — propuesta: eliminar `run` ambiguo para forzar elección consciente.
- Alternativas consideradas:
  - Variable de entorno `TARGET=...`: descartada, los flags CLI son más explícitos y discoverables.
  - Auto-detectar leyendo qué stack está corriendo: descartada, frágil (ambos pueden estar arriba).

### D7b: Generador de carga sintética
- Subdirectorio `load-generator/` con tres archivos:
  - `random_changes.py`: cliente Python que se conecta a `127.0.0.1:3306` (primario, expuesto al host) con `PyMySQL` y, en bucle, ejecuta una operación aleatoria por iteración (INSERT con datos sintéticos, UPDATE de email sobre una fila aleatoria, o DELETE de una fila aleatoria) sobre `inventory.customers`. Intervalo: 10 segundos. Detiene cuando el usuario pulsa **C** o envía SIGINT/SIGTERM.
  - `requirements.txt`: pin a `PyMySQL==1.1.1` (driver puro Python, sin dependencias de compilación).
  - `Makefile`: targets `venv` (crea `.venv/` con `python3.12 -m venv` e instala `requirements.txt`) y `venv-clean` (`rm -rf .venv`). Target adicional `run` para ejecutar el generador.
- Detección de tecla **C**: usar `termios.cbreak` + thread que lee `sys.stdin` (sin necesidad de Enter). Fallback: si stdin no es TTY (ejecución por pipe/background), solo escucha SIGINT/SIGTERM.
- Alternativas consideradas:
  - `mysql-connector-python` (oficial Oracle): descartado, requiere wheel binario y añade fricción al `pip install` en algunas distros. `PyMySQL` es pure Python.
  - Faker para datos sintéticos: descartado, mantiene `requirements.txt` con una sola dep; los nombres se eligen de listas hardcoded.
  - Ejecutar el generador como contenedor extra en `docker-compose`: descartado, el usuario quiere ejecutarlo desde su shell (con teclado interactivo) y `make` es el flujo natural.
- Por qué Python 3.12: pedido explícito del usuario; no usa features 3.12-específicas, así que también funcionaría con 3.11+.

### D7: Credenciales y puertos
- Contraseñas hardcodeadas en `docker-compose.yml` (este es un entorno de pruebas local). Variables: `MYSQL_ROOT_PASSWORD=root`, usuario `debezium/dbz`, usuario `repl/repl`.
- Puertos publicados al host: `mysql-primary` → 3306, `mysql-replica` → 3307. Debezium no necesita puerto publicado para este escenario, pero se expone 8080 opcionalmente para el endpoint de health.
- Se documenta cómo cambiarlos en el README.

## Risks / Trade-offs

- **Riesgo**: La réplica todavía está aplicando el snapshot inicial cuando Debezium intenta hacer su `INITIAL` snapshot, lo que puede provocar lecturas inconsistentes. → **Mitigación**: healthcheck de la réplica que confirma que la replicación está corriendo + Debezium con `snapshot.mode=initial` espera a través de `depends_on`.
- **Riesgo**: Debezium con `snapshot.mode=initial` toma `FLUSH TABLES WITH READ LOCK` sobre la **réplica**, lo que podría detener su SQL thread momentáneamente. → **Mitigación**: aceptable en escenario de demo; documentar y ofrecer `snapshot.mode=schema_only` como alternativa en el README.
- **Riesgo**: Diferencia de `server-id` entre nodos mal configurada rompe la replicación silenciosamente. → **Mitigación**: fijar `server-id=1` y `server-id=2` explícitamente en los `my.cnf` y verificar en el README con `SHOW SLAVE STATUS\G`.
- **Riesgo**: `log_slave_updates` no está activo y Debezium no ve los eventos replicados (es la causa #1 de fallo en este patrón). → **Mitigación**: lo declaramos explícitamente en `mysql/replica/my.cnf` y se valida en una scenario del spec.
- **Trade-off**: El sink `log` no permite reprocesar ni inspeccionar offsets fácilmente; los offsets se guardan en un fichero local dentro del contenedor de Debezium. Aceptable para demo; documentar el path para que el usuario pueda borrarlo y forzar re-snapshot.
- **Trade-off**: Sin volúmenes persistentes, cada `docker compose down -v` borra el estado y la réplica se vuelve a sincronizar desde cero. Esto es deseable para pruebas pero hay que dejarlo claro en el README.

## Migration Plan

No aplica: el escenario es nuevo y aislado, sin código existente que migrar. Para limpiar/reiniciar: `docker compose down -v` desde `withReplica/`.

## Open Questions

- ¿Conviene añadir un cuarto servicio `mysql-client` (imagen ligera con `mysql` CLI) para que el README pueda invocar `docker compose run --rm mysql-client ...` sin requerir cliente local? → Decisión propuesta: sí, lo incluimos para reducir fricción; si añade complejidad, se elimina al implementar.
- ~~¿Versión exacta de Debezium Server?~~ → Resuelto: `debezium/server:2.4.2.Final`. Verificada disponibilidad en Docker Hub y compatibilidad con MySQL 5.7 según la matriz oficial (<https://debezium.io/releases/2.4/>).
