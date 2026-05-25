## 1. Estructura

- [x] 1.1 Crear directorio `withReplica/monitoring/`
- [x] 1.2 Decidir si extraer un `_common.sh` (sourced) o mantener cada script self-contained — basado en el tamaño del código duplicado tras escribir el primero

## 2. Script para mysql5.7

- [x] 2.1 Crear `withReplica/monitoring/monitor-mysql5.7.sh` con shebang `#!/usr/bin/env bash` y `set -euo pipefail`
- [x] 2.2 Implementar parsing de flags: `-i SECONDS` (default 5), `-d SECONDS` (opcional), `--csv` (opcional), `-h` (ayuda)
- [x] 2.3 Implementar función `check_container` que verifica vía `docker inspect mysql-replica` y aborta con mensaje claro + exit 2 si no existe
- [x] 2.4 Implementar `read_docker_stats` que llama `docker stats --no-stream --format '{{...}}' mysql-replica` y extrae BlockIO read/write, NetIO rx/tx, CPU%, MemUsage
- [x] 2.5 Implementar `read_mysql_status` que ejecuta `mysql -h 127.0.0.1 -P 3307 -uroot -proot -N -e "SHOW GLOBAL STATUS WHERE Variable_name IN (...)"` y captura los counters listados en design D3
- [x] 2.6 Implementar lógica de **delta**: guardar la muestra anterior; primera iteración se etiqueta `baseline`, las siguientes reportan `(actual - anterior) / intervalo` en bytes/seg
- [x] 2.7 Implementar formato de salida humano (alineado, sufijos K/M, header cada 20 filas) y CSV (header una vez)
- [x] 2.8 Trap de `SIGINT`/`SIGTERM` que imprime una línea de cierre (timestamp + exit 0)
- [x] 2.9 Manejo de fallos en MySQL: si una iteración falla, log a stderr, marcar columnas MySQL con `?` y continuar
- [x] 2.10 Marcar el script como ejecutable (`chmod +x`)

## 3. Script para mysql8

- [x] 3.1 Crear `withReplica/monitoring/monitor-mysql8.sh` partiendo de la versión 5.7, ajustando:
  - Nombre del contenedor: `mysql8-replica` (no `mysql-replica`)
  - Puerto host: 3309 (no 3307)
  - Label en la salida: `mysql8` (no `mysql5.7`)
- [x] 3.2 Si tras 3.1 hay >30 líneas duplicadas con el script de 5.7, refactorizar a `_common.sh` y dejar ambos scripts como `source ./_common.sh; STACK=mysql5.7|mysql8; main "$@"`
- [x] 3.3 Marcar el script como ejecutable

## 4. Documentación

- [x] 4.1 Crear `withReplica/monitoring/README.md` con:
  - Pre-requisitos (docker, mysql CLI, jq opcional, los stacks corriendo)
  - Comandos básicos: `./monitor-mysql5.7.sh`, `./monitor-mysql8.sh --csv -i 5 -d 60 | tee /tmp/mysql8.csv`
  - Flujo de medición end-to-end junto al load-generator (terminal A: monitor con `tee`; terminal B: `make run-8`)
  - Tabla de columnas de salida con su significado y unidad
  - Notas sobre interpretación: por qué `BlockIO` puede no coincidir con `Innodb_data_*`, qué significa que `Binlog_cache_disk_use` sea > 0
  - Troubleshooting: contenedor no existe; error de auth; timestamps desalineados al intercalar dos scripts
- [x] 4.2 Añadir sección breve en `withReplica/README.md` top-level que enlace al README de monitoring

## 5. Verificación end-to-end

- [x] 5.1 Levantar el stack mysql5.7 (`cd mysql5.7 && docker compose up -d`)
- [x] 5.2 Ejecutar `./monitoring/monitor-mysql5.7.sh -d 30 -i 5` durante el snapshot inicial de Debezium; confirmar que la primera línea es `baseline`, las siguientes tienen valores numéricos en todas las columnas y el script termina solo a los ~30s
- [x] 5.3 Repetir con `--csv` y validar que el output puede importarse en una hoja de cálculo (header parseable, comas consistentes)
- [x] 5.4 Mientras corre el monitor, lanzar `cd load-generator && make run-5.7` y confirmar que las métricas `Innodb_data_read` e `Innodb_data_written` o `Bytes_sent` muestran un incremento detectable durante las operaciones (delta no nulo)
- [x] 5.5 Repetir 5.1–5.4 con el stack mysql8 (`cd mysql8 && ...`, `monitor-mysql8.sh`, `make run-8`)
- [x] 5.6 Apagar uno de los stacks y ejecutar su script de monitoreo; confirmar mensaje de error claro sobre contenedor faltante y exit code != 0
- [x] 5.7 Probar `Ctrl+C`: verificar que el script imprime cierre limpio y termina con exit 0

## 6. Visualización con Python (`monitoring/plot/`)

- [x] 6.1 Crear `withReplica/monitoring/plot/` con `requirements.txt` (`pandas`, `matplotlib` con versiones pinneadas)
- [x] 6.2 Crear `monitoring/plot/Makefile` con targets `venv`, `venv-clean`, y `plot` (recibe `CSVS=...` como variable). Patrón análogo al `Makefile` de `load-generator/`
- [x] 6.3 Implementar `monitoring/plot/plot.py` con:
  - argparse: positional `CSV` (1 o 2 archivos), `-o OUT` (default `monitoring-report.png`), `--title TEXT`, `--smooth N`
  - Lectura con `pandas.read_csv`; manejo de error si el archivo no existe o el header no contiene las columnas esperadas (exit 2 con mensaje claro)
  - Cálculo de tiempo relativo desde la primera muestra de cada CSV (segundos transcurridos)
  - Filtrado de la fila `baseline` (sin valor numérico)
  - Grid de subplots (matplotlib `subplots(3, 2)` o similar): BlockIO read, BlockIO write, NetIO tx, Innodb_data_read, Innodb_data_written, Bytes_sent (CPU% como overlay si queda espacio o panel propio)
  - Cuando hay 2 CSVs, etiquetas tomadas de la columna `stack` del CSV
  - `--smooth N` aplica `rolling(N).mean()`
  - `plt.savefig(out_path, dpi=120, bbox_inches='tight')`
- [x] 6.4 Documentar en `monitoring/README.md` el flujo end-to-end:
  ```
  ./monitor-mysql5.7.sh --csv -d 60 | tee /tmp/m57.csv
  ./monitor-mysql8.sh --csv -d 60 | tee /tmp/m8.csv
  cd plot && make venv && make plot CSVS="/tmp/m57.csv /tmp/m8.csv"
  ```
- [x] 6.5 Verificación: capturar 60s de cada stack durante load-generator, ejecutar `make plot`, abrir el PNG y confirmar que se ven dos series superpuestas con diferencia visible cuando hay carga; confirmar que con un solo CSV se ve una serie sola
- [x] 6.6 Verificar manejo de error: pasar un CSV inexistente y confirmar exit code != 0 + mensaje claro