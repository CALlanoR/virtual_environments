## Context

Los dos stacks (`mysql5.7/`, `mysql8/`) corren localmente en Docker. Debezium Server se conecta a la réplica de cada stack y, según el modo, hace snapshot inicial (lectura masiva de tablas) y luego streaming de binlog (lectura continua de archivos `mysql-bin.NNNNNN`). Necesitamos cuantificar el I/O de cada fase **sin instrumentar Debezium ni MySQL**, usando solo lo observable desde fuera del contenedor (Docker) y desde sus métricas internas (`SHOW GLOBAL STATUS` y `performance_schema`).

El objetivo del cambio es producir una traza temporal (timestamp + métricas) que el usuario pueda capturar en un archivo CSV mientras corre el `load-generator`, y comparar después entre stacks.

## Goals / Non-Goals

**Goals:**
- Un script por stack, ejecutable directamente (no requiere venv ni build).
- Métricas relevantes para "qué tan intensivo es el I/O en la réplica": bytes leídos/escritos a disco, bytes salientes hacia Debezium, contadores de binlog.
- Salida útil para inspección rápida (humano) y para análisis posterior (CSV).
- Tolerante a errores transitorios (un docker stats que falla no debe matar el bucle).

**Non-Goals:**
- Dashboards (Grafana, Prometheus). Si el usuario quiere graficar, importa el CSV en una hoja de cálculo o pandas.
- Métricas de Debezium Server en sí (JMX, etc.). El alcance es solo la réplica MySQL — del lado consumidor de los binlogs.
- Métricas a nivel de query individual (qué query hizo Debezium). Sería útil pero requiere `general_log` o `performance_schema` con setup específico; fuera de scope.
- Soporte multi-OS para los scripts. Linux + bash; el resto del repo asume lo mismo.
- Comparación automática entre stacks. El script genera datos; la comparación la hace el usuario.

## Decisions

### D1: Bash, no Python
- Los scripts no requieren parsing complejo ni dependencias; `docker`, `mysql`, `awk` son suficientes.
- Bash evita el venv adicional y mantiene el flujo "clonas y corres".
- Alternativa considerada: Python + `docker` SDK + `pymysql`. Descartada — añade un segundo venv y la complejidad no se justifica para una traza periódica de métricas.

### D2: Ubicación y nombres
- `withReplica/monitoring/`
  - `monitor-mysql5.7.sh`
  - `monitor-mysql8.sh`
  - `_common.sh` (sourced) si la duplicación entre los dos scripts pasa de ~30 líneas. Decisión final en implementación.
  - `README.md`
- Los scripts son ejecutables (`chmod +x`) y tienen shebang `#!/usr/bin/env bash`.

### D3: Métricas a recolectar y de dónde

**Capa contenedor (`docker stats --no-stream --format`):**
- `BlockIO`: bytes leídos/escritos al filesystem del host por el contenedor MySQL. Es la mejor proxy de I/O físico.
- `NetIO`: bytes entrantes/salientes; el saliente refleja lo que MySQL le envía a Debezium (binlog stream + protocolo).
- `CPU%` y `MemUsage`: contexto de carga.

**Capa MySQL (`SHOW GLOBAL STATUS` vía `mysql -h 127.0.0.1 -P <puerto> -uroot -proot -N -e`):**
- `Innodb_data_read`, `Innodb_data_written`: bytes a/desde el InnoDB engine.
- `Innodb_data_reads`, `Innodb_data_writes`: número de operaciones (para calcular avg size).
- `Bytes_received`, `Bytes_sent`: tráfico de red a nivel del protocolo MySQL. `Bytes_sent` es el dato más directo de "cuánto está enviando la réplica a Debezium".
- `Binlog_cache_use`, `Binlog_cache_disk_use`: para detectar si el binlog cache se desborda a disco (relevante en cargas altas).
- Versión-específico:
  - 5.7: `Slave_open_temp_tables`, `Com_show_slave_status` (no críticos pero útiles).
  - 8.0: equivalentes con prefijo `Replica_*` cuando existan.

**Counters acumulativos vs delta:**
- `SHOW GLOBAL STATUS` reporta valores acumulados desde el último restart. El script DEBE calcular **delta** entre iteraciones para que el dato sea "tasa por intervalo", que es lo que importa.
- En la primera iteración no hay delta posible — se imprime fila marcada como `baseline` o se omite.

### D4: Interfaz CLI

```
monitor-mysql<X>.sh [-i SECONDS] [-d SECONDS] [--csv] [-h]

  -i N        Intervalo entre muestras en segundos (default: 5).
  -d N        Duración total en segundos. Si se omite, corre hasta Ctrl+C.
  --csv       Emite CSV (con header en la primera línea). Default: human-readable.
  -h          Ayuda.
```

Ambos scripts comparten flags. Lo único que cambia entre ellos es:
- El nombre del contenedor objetivo (`mysql-replica` vs `mysql8-replica`).
- El puerto host de MySQL (`3307` vs `3309`).
- El label que aparece en la salida (`mysql5.7` vs `mysql8`).

### D5: Formato de salida

**CSV (con `--csv`):**
```
timestamp,stack,cpu_pct,mem_mb,blkio_read_bytes,blkio_write_bytes,netio_rx_bytes,netio_tx_bytes,innodb_read_bps,innodb_write_bps,mysql_bytes_sent_bps,binlog_cache_use_delta,binlog_cache_disk_use_delta
2026-05-07T16:30:00,mysql5.7,3.4,512,0,0,0,0,baseline,baseline,baseline,baseline,baseline
2026-05-07T16:30:05,mysql5.7,4.1,514,0,8192,1024,40960,0,1638,8192,2,0
...
```

**Human-readable (default):**
- Header cada N filas (e.g., cada 20) para facilitar lectura larga.
- Columnas alineadas; bytes en KB/MB con sufijos.
- Línea de baseline marcada con `[baseline]`.

### D6: Manejo de errores

- Si `docker inspect <container>` falla → mensaje claro `"Container <X> no encontrado. ¿El stack está arriba?"`, exit 2.
- Si `mysql` falla en una iteración → log a stderr, esa muestra con métricas MySQL marcadas como `?` pero el bucle continúa (no abortar — el contenedor podría estar momentáneamente saturado).
- `Ctrl+C` → cierre limpio (trap SIGINT/SIGTERM), imprime una línea final con resumen (mín/máx/avg de las métricas más importantes).

### D7: Cómo se usa junto al load-generator

Flujo recomendado en el README:
1. Levantar el stack: `cd mysql8 && docker compose up -d`.
2. Esperar a que esté `healthy`.
3. En una terminal: `monitoring/monitor-mysql8.sh --csv -i 5 | tee /tmp/mysql8-io.csv`.
4. En otra terminal: `cd load-generator && make run-8`.
5. Tras unos minutos, parar ambos y comparar.

Alternativa considerada: un script "wrapper" que coordine load-generator + monitor en un solo comando. Descartada — acopla cosas que el usuario querrá variar independientemente.

### D8: Visualización offline con pandas + matplotlib

- **Ubicación**: `withReplica/monitoring/plot/` con `plot.py`, `requirements.txt` y `Makefile` propios. **Venv separado** del de `load-generator/` porque las dependencias son disjuntas (PyMySQL+cryptography vs pandas+matplotlib) y queremos que cada herramienta evolucione sin acoplarse.
- **Input**: **uno o dos** CSVs (positional args). Cuando son dos, se asume comparación entre stacks; el `stack` reportado en la columna del CSV se usa como label de la leyenda.
- **Output**: PNG (default `monitoring-report.png` en cwd; flag `-o` para sobrescribir).
- **Alineación temporal**: por **tiempo relativo** desde la primera muestra de cada CSV. Esto permite comparar capturas hechas en momentos distintos (e.g., medí 5.7 ayer y 8 hoy, ambos durante 60s de carga).
- **Layout**: grid de subplots (3×2 ó 2×3 según se vea mejor):
  - BlockIO read rate, BlockIO write rate
  - NetIO tx rate (lo que sale hacia Debezium)
  - `Innodb_data_read` rate, `Innodb_data_written` rate
  - `Bytes_sent` rate (MySQL protocol)
  - CPU%
- **CLI**:
  ```
  plot.py CSV [CSV2] [-o OUT.png] [--title TEXT] [--smooth N]
  ```
  - `--smooth N` aplica rolling mean de N muestras (útil cuando el intervalo es 1s y hay ruido).
- **Targets `Makefile`**:
  - `make venv` / `make venv-clean` (paralelo al patrón de `load-generator/`).
  - `make plot CSVS="path1.csv path2.csv"` — pasa los CSVs al script. Doc en `make help`.
- **Alternativas consideradas**:
  - Plotly HTML interactivo: descartado para esta iteración — un PNG estático es suficiente para el caso "ver un reporte y guardarlo en un PR/notebook".
  - Reusar el venv de `load-generator/`: descartado — meter pandas+matplotlib en él (~150MB) ralentiza el setup del generador, que debe permanecer ligero.
  - Generar SVG en lugar de PNG: descartado por defecto — PNG es trivial de pegar en herramientas de chat/issues; el usuario puede pasar `-o report.svg` si su matplotlib backend lo soporta.

## Risks / Trade-offs

- **Riesgo**: `docker stats` consume ~1-2% CPU del host por iteración; con `-i 1` (intervalo 1s) puede ser ruido al medir un sistema ya saturado. → **Mitigación**: default `-i 5`. Documentar el trade-off.
- **Riesgo**: `SHOW GLOBAL STATUS` se acumula desde el último `FLUSH STATUS` o restart del servidor. Si el contenedor lleva días corriendo, los valores absolutos son grandes. → **Mitigación**: la salida muestra **deltas** entre iteraciones, no absolutos. La primera iteración se marca como `baseline`.
- **Riesgo**: `BlockIO` reportado por Docker es read/write desde el contenedor al storage; en algunos drivers (overlay2, sin volúmenes externos) las escrituras pueden no reflejar lo que va a disco "real". → **Mitigación**: documentar que es un proxy y combinarlo con `Innodb_data_*` y `Bytes_sent` para un cuadro más completo.
- **Trade-off**: con `--csv`, los headers solo aparecen una vez (en la primera línea). Si redirigís a un archivo y reinicias el script, el segundo header se concatena al final. Aceptable; documentado.
- **Trade-off**: scripts duplican ~70% de su código entre los dos stacks. Si se evita un `_common.sh`, el copy/paste es legible y self-contained; si se extrae, hay un único punto de cambio pero los scripts dejan de ser "un archivo y se corre". Decisión final en implementación según el largo final.

## Migration Plan

No aplica: capability nueva, no afecta nada existente. Para usar:

```bash
chmod +x withReplica/monitoring/monitor-mysql5.7.sh withReplica/monitoring/monitor-mysql8.sh
./withReplica/monitoring/monitor-mysql8.sh --csv -i 5 | tee mysql8-io.csv
```

## Open Questions

- ¿Conviene dejar la duración por defecto infinita (Ctrl+C) o forzar a pasar `-d`? → Decisión propuesta: infinita con Ctrl+C; el usuario puede pasar `-d` cuando quiera capturar exactamente N segundos.
- ¿Algún flag para invocar `FLUSH STATUS` antes de empezar y arrancar con counters limpios? → Decisión propuesta: sí, flag `--reset` opcional. Útil cuando se quiere medir desde un evento conocido (e.g., justo antes del snapshot inicial). Lo añadimos si no complica la implementación; si crece, queda para un change futuro.
