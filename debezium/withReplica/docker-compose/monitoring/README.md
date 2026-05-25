# `monitoring/` — I/O en las réplicas MySQL

Herramientas para cuantificar **qué tan intensivo es Debezium en I/O** sobre las réplicas de los stacks `mysql5.7/` y `mysql8/`.

Tres componentes:

| Archivo | Para qué |
| --- | --- |
| `monitor-mysql5.7.sh` | Captura periódica de métricas del contenedor `mysql-replica` (stack 5.7) |
| `monitor-mysql8.sh`   | Lo mismo para `mysql8-replica` (stack 8) |
| `plot/` (Python)      | Toma uno o dos CSVs y genera un PNG con paneles comparativos |

Los scripts bash son **read-only**: solo leen `docker stats` y `SHOW GLOBAL STATUS`.

## Pre-requisitos

- `docker` CLI funcional.
- `awk` (presente en cualquier distro estándar).
- Para el plot: `python3.12` (el script bash funciona sin él).
- **No se necesita cliente `mysql` en el host** — los scripts ejecutan el cliente dentro del contenedor vía `docker exec`.
- El stack que vas a monitorear debe estar `up` (`docker compose ps` muestra el contenedor sano).

## Quickstart: comparar 5.7 vs 8 con un solo comando

Si lo único que quieres es **el PNG comparativo**, usa el orquestador:

```bash
# 1. Pre-requisitos (una sola vez)
cd withReplica/load-generator   && make venv     # PyMySQL + cryptography
cd ../monitoring/plot           && make venv     # pandas + matplotlib
cd ../..

# 2. Levantar ambos stacks
make up && make wait-healthy

# 3. Lanzar la comparación (corre ~80s y termina solo)
./monitoring/run-comparison.sh

# 4. Ver el resultado
xdg-open /tmp/comparison.png

# 5. Bajar los stacks
make down
```

`run-comparison.sh` orquesta el flujo completo:

```
t=0    arrancan ambos monitores (-i 1 -d 80)
t=20   arrancan ambos random_changes.py (-i 1 -d 40)
t=60   los generadores auto-terminan (40 ops cada uno)
t=80   los monitores auto-terminan
t=80+  se genera /tmp/comparison.png
```

Outputs: `/tmp/mysql57.csv`, `/tmp/mysql8.csv` y `/tmp/comparison.png`.

### Overrides

Variables de entorno (todas opcionales):

| Variable | Default | Significado |
| --- | --- | --- |
| `PRELOAD_S` | 20 | Segundos de baseline antes de la carga |
| `LOAD_S` | 40 | Duración de la carga |
| `POSTLOAD_S` | 20 | Cooldown después de la carga |
| `INTERVAL_MONITOR` | 1 | Intervalo del monitor (segundos) |
| `CSV57` | `/tmp/mysql57.csv` | Path del CSV de mysql5.7 |
| `CSV8` | `/tmp/mysql8.csv` | Path del CSV de mysql8 |
| `OUT` | `/tmp/comparison.png` | Path del PNG resultante |

Ejemplos:

```bash
# Run rápido para dev (~20s)
LOAD_S=10 PRELOAD_S=5 POSTLOAD_S=5 ./monitoring/run-comparison.sh

# Run largo para análisis serio (~5 min)
LOAD_S=180 PRELOAD_S=60 POSTLOAD_S=60 OUT=/tmp/long-run.png ./monitoring/run-comparison.sh
```

### Pre-flight automático

El orquestador valida antes de empezar:
- Ambos contenedores `mysql-replica` y `mysql8-replica` corriendo (no solo creados).
- Venvs presentes en `load-generator/.venv/` y `monitoring/plot/.venv/`.

Si algo falta, sale con exit 2 y mensaje accionable, sin gastar 80s.

## Uso manual / debug

Para iterar sobre un solo stack, depurar una métrica concreta o capturar fuera de la ventana de 80s, los componentes individuales también funcionan a mano. Ejemplo con un solo stack (mysql8):

```bash
# Una terminal: monitor con CSV
./monitoring/monitor-mysql8.sh --csv -i 3 -d 90 | tee /tmp/mysql8.csv

# Otra terminal: generador con la duración que quieras
load-generator/.venv/bin/python load-generator/random_changes.py --target mysql8 -i 1 -d 60

# Plot manual
cd monitoring/plot
make plot CSVS="/tmp/mysql8.csv" OUT=/tmp/single.png
```

Notas:
- `random_changes.py` ahora **auto-termina** tras la duración (default 40s). Pásale `-d 0` si quieres el comportamiento antiguo (correr hasta `C`/`Ctrl+C`).
- El monitor también auto-termina si pasas `-d N`. Sin `-d` corre hasta `Ctrl+C`.

## Uso básico

```bash
# Modo human-readable (default), intervalo 5s, hasta Ctrl+C:
./monitor-mysql8.sh

# Modo CSV, intervalo 3s, durante 60s, salida a archivo:
./monitor-mysql8.sh --csv -i 3 -d 60 | tee /tmp/mysql8.csv
```

Flags (idénticos en ambos scripts):

| Flag | Default | Significado |
| --- | --- | --- |
| `-i N`  | 5  | Intervalo entre muestras (segundos) |
| `-d N`  | ∞  | Duración total. Si se omite, corre hasta SIGINT |
| `--csv` | off | Emite CSV con header en la primera línea (apto para `tee` y plotear) |
| `-h`    |    | Ayuda |

## Columnas de salida

Las métricas reportadas (excepto la primera fila marcada `baseline`) son **tasas por segundo** calculadas como `(actual - anterior) / interval`.

| Columna (CSV)               | Columna (humano) | Origen | Interpretación |
| --- | --- | --- | --- |
| `cpu_pct`                   | `cpu%`     | `docker stats` | % CPU usado por el contenedor MySQL |
| `mem_bytes`                 | `mem`      | `docker stats` | RSS actual del contenedor |
| `blkio_read_bps`            | `blk_r/s`  | `docker stats BlockIO` | Bytes/seg leídos del filesystem por el contenedor (proxy de I/O físico) |
| `blkio_write_bps`           | `blk_w/s`  | `docker stats BlockIO` | Bytes/seg escritos (binlog growth, datafiles, redo log) |
| `netio_rx_bps`              | (no en humano) | `docker stats NetIO` | Bytes/seg entrantes al contenedor |
| `netio_tx_bps`              | `net_tx/s` | `docker stats NetIO` | Bytes/seg salientes (≈ lo que Debezium pulla más overhead TCP) |
| `innodb_read_bps`           | `innodb_r/s` | `SHOW GLOBAL STATUS` `Innodb_data_read` | Bytes/seg leídos por el motor InnoDB |
| `innodb_write_bps`          | `innodb_w/s` | `SHOW GLOBAL STATUS` `Innodb_data_written` | Bytes/seg escritos por InnoDB |
| `mysql_bytes_sent_bps`      | `mysql_tx/s` | `SHOW GLOBAL STATUS` `Bytes_sent` | Bytes/seg que MySQL envía al protocol (≈ payload Debezium-pull) |
| `mysql_bytes_recv_bps`      | `mysql_rx/s` | `SHOW GLOBAL STATUS` `Bytes_received` | Bytes/seg recibidos (escritura desde load-generator vía replicación) |
| `binlog_cache_use_delta`    | `bnlc`     | `Binlog_cache_use` | Transacciones nuevas que usaron el cache de binlog (no es bps; es count delta) |
| `binlog_cache_disk_use_delta` | (no en humano) | `Binlog_cache_disk_use` | Transacciones que se desbordaron a disco. Si > 0 → cache pequeño |

### Notas de interpretación

- **`BlockIO` vs `Innodb_data_*`**: `BlockIO` es lo que el contenedor le pide al filesystem (incluye writes a binlog, redo log, ibtmp, etc.); `Innodb_data_*` es solo lo que pasa por el InnoDB engine (no cuenta binlog). Ver ambos da una imagen más completa.
- **`mysql_bytes_sent_bps`** es el dato más directo de "cuánto le envía la réplica a Debezium". Pero incluye también el overhead del protocolo (heartbeats del replication thread interno — la réplica habla con su master a cada poco).
- **Primera muestra es `baseline`** — no hay delta posible. Las tasas reales empiezan en la segunda iteración.
- **Si una iteración falla** (timeout, contenedor saturado), las columnas MySQL aparecen como `?` y el bucle continúa.

## Flujo end-to-end con carga real

En tres terminales:

**T1** — monitor del stack 8 (CSV):
```bash
cd withReplica/monitoring
./monitor-mysql8.sh --csv -i 3 -d 90 | tee /tmp/mysql8.csv
```

**T2** — generador de carga contra el mismo stack:
```bash
cd withReplica/load-generator
make venv     # si es la primera vez
make run-8    # presiona C para parar
```

**T3** — observador opcional de eventos CDC en tiempo real:
```bash
cd withReplica/mysql8
docker compose logs -f cdc-sink
```

Repite contra el stack 5.7 (`monitor-mysql5.7.sh`, `make run-5.7`) para una segunda traza. Ambas trazas pueden capturarse en momentos distintos — el plot las alinea por **tiempo relativo**.

## Visualización

```bash
cd withReplica/monitoring/plot
make venv                                                    # primera vez, instala pandas + matplotlib
make plot CSVS="/tmp/mysql57.csv /tmp/mysql8.csv" OUT=compare.png
make help                                                    # lista todos los targets
make venv-clean                                              # eliminar el venv si quieres
```

Genera un PNG con 6 paneles superponiendo las dos series (cuando se pasan dos CSVs):

| Panel | Métrica | Por qué importa |
| --- | --- | --- |
| BlockIO read | Bytes/seg leídos del filesystem | Lo que MySQL pide al disco. Picos durante snapshot inicial de Debezium. |
| BlockIO write | Bytes/seg escritos al filesystem | Crecimiento de binlog + redo log + datafiles |
| Innodb_data_read | Bytes/seg leídos por InnoDB | Solo lecturas del engine (no incluye binlog) |
| Innodb_data_written | Bytes/seg escritos por InnoDB | Mutaciones aplicadas (incluye replicación entrante) |
| MySQL Bytes_sent | Bytes/seg salientes a nivel protocolo MySQL | ≈ payload que Debezium consume del binlog |
| NetIO tx | Bytes/seg salientes del contenedor | Mismo concepto a nivel red. Incluye overhead TCP. |

Con un solo CSV se ve una sola serie en cada panel.

Flags adicionales del `plot.py` (también pasables vía la variable `OUT` del Makefile):

```
plot.py CSV1 [CSV2] [-o OUT] [--title TEXT] [--smooth N]
```

- `--smooth N` aplica rolling mean de tamaño N — útil cuando capturas con `-i 1` y hay ruido visual.
- `--title "..."` sobrescribe el supertítulo automático.

### Cómo leer los resultados

- **Snapshot inicial**: pico grande en `BlockIO read` y `Innodb_data_read` durante los primeros segundos después de arrancar Debezium contra una réplica vacía. Magnitud proporcional al tamaño de las tablas en `table.include.list`.
- **Streaming continuo (sin carga)**: `BlockIO`/`Innodb_*` casi planos. `MySQL Bytes_sent` no es cero — la réplica habla con su master vía replication thread (heartbeats), y Debezium hace polls regulares al binlog.
- **Streaming con carga**: cada operación del load-generator se ve como un escalón pequeño en `BlockIO write` (binlog growth) e `Innodb_data_written` (datafile mutations).
- **Diferencias 5.7 vs 8**: típicamente `BlockIO write` es más alto en 8.0 por cambios de formato de redo log; `Bytes_sent` puede ser similar porque el protocolo binlog cambió poco. Si ves un panel con diferencias grandes, vale la pena investigar — puede ser una optimización en uno u otro engine.

## Troubleshooting

### `Error: contenedor 'X' no encontrado`
El stack no está arriba o tiene otro `container_name`. Comprueba con `docker compose ps` desde el directorio del stack correspondiente.

### `Error: contenedor 'X' existe pero está detenido`
Existe pero no está corriendo. Arráncalo: `docker compose up -d` desde el directorio del stack.

### Columnas MySQL en `?`
La consulta `docker exec ... mysql ...` falló (timeout, contenedor saturado). El bucle continúa; si persiste, mira `docker compose logs <replica>`.

### CSV vacío
Si redirigís `>` (no `tee`), no verás nada hasta el cierre. Usa `tee` para ver progreso en pantalla y guardar a archivo a la vez.

### Timestamps desalineados al graficar dos CSVs
No es un problema: el plot alinea por tiempo relativo (segundos desde la primera muestra de cada CSV). Si capturaste 60s del stack 5.7 ayer y 60s del stack 8 hoy, los dos gráficos arrancan en t=0.

### `docker stats` añade ~1s de overhead por iteración
Conocido. Por eso el default de `-i` es 5s — el ruido relativo es aceptable. Con `-i 1` el sampling se acerca al overhead y los datos se vuelven menos confiables.
