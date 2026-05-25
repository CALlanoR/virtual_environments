## Why

Después de validar end-to-end los dos stacks (`mysql5.7/` y `mysql8/`) queremos cuantificar **qué tan intensivo es Debezium Server en I/O** sobre las réplicas. Esto sirve para:

- Saber el orden de magnitud de bytes/seg leídos del disco de la réplica durante (a) snapshot inicial y (b) streaming continuo de binlog.
- Comparar 5.7 + Debezium 2.4.2.Final vs 8.0 + Debezium 3.5.0.Final bajo la misma carga (la del `load-generator`), para identificar diferencias de eficiencia entre versiones.
- Tener una herramienta repetible que sirva de baseline para futuros experimentos (cambios en `snapshot.mode`, en `table.include.list`, en throughput de escritura, etc.).

Hoy no existe ningún script para esto: el usuario solo dispone de `docker stats` manual y consultas SQL ad-hoc.

## What Changes

- Añadir un subdirectorio `withReplica/monitoring/` con **dos scripts bash**, uno por stack:
  - `monitor-mysql5.7.sh` — monitorea I/O del contenedor `mysql-replica` del stack 5.7.
  - `monitor-mysql8.sh` — monitorea I/O del contenedor `mysql8-replica` del stack 8.
- Cada script, en bucle (intervalo configurable, default 5s), recolecta y emite por stdout:
  - Métricas a nivel contenedor (`docker stats --no-stream`): `BlockIO read/write`, `NetIO in/out`, `CPU%`, `Mem`.
  - Métricas a nivel MySQL (`SHOW GLOBAL STATUS`): `Innodb_data_read`, `Innodb_data_written`, `Bytes_sent`, `Bytes_received`, `Binlog_cache_use`, `Binlog_cache_disk_use`, y los counters específicos de cada versión.
  - Cada línea con timestamp ISO-8601.
- Modos de salida: por defecto formato legible para humanos (alineado, headers); con flag `--csv` emite CSV apto para `tee` a archivo y graficar después.
- Intervalo configurable con `-i N` (segundos). Termina con `Ctrl+C` o tras `-d N` segundos si se pasa duración.
- Detección y manejo de errores razonable: si el contenedor objetivo no existe, mensaje claro y exit code != 0.
- Documentar en un `monitoring/README.md` cómo correrlo en paralelo al `load-generator` para obtener una traza comparable entre los dos stacks.
- Añadir un **script Python de visualización** en `withReplica/monitoring/plot/` (con su propio venv y `Makefile`) que tome **uno o dos CSVs** generados por los scripts bash y produzca un PNG con grid de paneles (BlockIO read/write, NetIO tx, Innodb_data_read/written, Bytes_sent, CPU%) alineados por tiempo relativo. Cuando recibe dos CSVs, los superpone en el mismo eje para comparar 5.7 vs 8 lado a lado.

## Capabilities

### New Capabilities
- `replica-io-monitoring`: herramientas (un script por stack) para monitorear el consumo de I/O de la réplica MySQL mientras Debezium Server está leyendo sus binlogs, mostrando métricas de contenedor y de MySQL.

### Modified Capabilities
<!-- N/A: no modificamos requirements de mysql-replica-debezium-test; añadimos una capability complementaria. -->

## Impact

- Código nuevo bajo `withReplica/monitoring/`:
  - Dos scripts bash (uno por stack) + `README.md` + posiblemente `_common.sh` si hay duplicación significativa.
  - Subdirectorio `plot/` con `plot.py`, `requirements.txt` (pandas, matplotlib) y `Makefile` (targets `venv`, `venv-clean`, `plot`).
- Sin cambios en `mysql5.7/`, `mysql8/`, ni `load-generator/`. Las herramientas son **read-only** sobre los stacks.
- Dependencias externas:
  - Bash scripts: `docker` CLI, `mysql` CLI, `awk`. Sin Python.
  - Plot script: `python3.12`, `pandas`, `matplotlib` (en su propio venv para no contaminar el de `load-generator/`).
- Acceso a las réplicas: los scripts bash se conectan al puerto host correspondiente (3307 para 5.7, 3309 para 8) usando el usuario `root`.
- No introduce dependencias nuevas en imágenes Docker.
