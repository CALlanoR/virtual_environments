## 1. Modificar `random_changes.py`

- [x] 1.1 Reemplazar la constante `INTERVAL_SECONDS = 10` por defaults vía argparse: `--interval N` (default 1) y `--duration N` (default 40)
- [x] 1.2 Implementar lógica de auto-stop: capturar `started_at = time.monotonic()` antes del loop; en cada iteración, si `(time.monotonic() - started_at) >= duration` Y `duration > 0`, hacer `stop_event.set()` y salir del loop
- [x] 1.3 Cuando `--duration 0` se pasa explícitamente, no aplicar el timer (modo infinito legacy)
- [x] 1.4 Actualizar el log de inicio para que mencione la duración elegida (e.g., `[hh:mm:ss] Generador iniciado. Cada 1s durante 40s. Presiona 'C' para parar antes.`)
- [x] 1.5 Verificar manualmente: `random_changes.py --target mysql5.7` (sin flags) corre exactamente ~40 ops y termina; `random_changes.py --target mysql5.7 -d 10` corre ~10 ops; `random_changes.py --target mysql5.7 -d 0` corre indefinidamente hasta SIGINT

## 2. Crear `withReplica/Makefile` (top-level)

- [x] 2.1 Crear `withReplica/Makefile` con `.PHONY` de todos los targets
- [x] 2.2 Implementar target `up`: `cd mysql5.7 && docker compose up -d`, luego mismo para `mysql8/`
- [x] 2.3 Implementar target `down`: `docker compose down -v` para ambos stacks (con `-v` intencional)
- [x] 2.4 Implementar target `ps` con encabezados que diferencien cada stack
- [x] 2.5 Implementar target `wait-healthy` que bloquee con `until docker compose ps --format json | grep -q '"Health":"healthy"' ...` para cada stack
- [x] 2.6 Implementar target `help` que liste los targets disponibles y mencione que el monitoreo es manual vía `monitoring/run-comparison.sh`
- [x] 2.7 Confirmar que NO hay un target que invoque el orquestador

## 3. Crear `monitoring/run-comparison.sh`

- [x] 3.1 Crear `withReplica/monitoring/run-comparison.sh` con shebang `#!/usr/bin/env bash` y `set -euo pipefail`
- [x] 3.2 Implementar parseo de `--help`/`-h` que muestre defaults
- [x] 3.3 Implementar pre-flight: verificar `mysql-replica` y `mysql8-replica` con `docker inspect -f '{{.State.Running}}'`; verificar venvs `load-generator/.venv/bin/python` y `monitoring/plot/.venv/bin/python`. Exit 2 con mensaje accionable si algo falta
- [x] 3.4 Definir variables con defaults: `PRELOAD_S=20`, `LOAD_S=40`, `POSTLOAD_S=20`, `INTERVAL_MONITOR=1`, `CSV57=/tmp/mysql57.csv`, `CSV8=/tmp/mysql8.csv`, `OUT=/tmp/comparison.png`. Permitir override vía env vars
- [x] 3.5 Calcular `TOTAL_S=$((PRELOAD_S + LOAD_S + POSTLOAD_S))` y lanzar ambos monitores en background con `-i $INTERVAL_MONITOR -d $TOTAL_S` redirigiendo a sus CSVs
- [x] 3.6 `sleep $PRELOAD_S` para baseline
- [x] 3.7 Lanzar ambos `random_changes.py` en background con `-i 1 -d $LOAD_S`
- [x] 3.8 `wait` para que ambos generadores terminen (auto-stop por duración)
- [x] 3.9 `wait` para que ambos monitores terminen (auto-stop por su propio `-d`)
- [x] 3.10 Llamar al plot vía `monitoring/plot/.venv/bin/python monitoring/plot/plot.py "$CSV57" "$CSV8" -o "$OUT"`
- [x] 3.11 Imprimir un resumen final con paths de los CSVs y el PNG generado
- [x] 3.12 Trap de SIGINT/SIGTERM que `kill` los hijos en background y aborta el plot
- [x] 3.13 `chmod +x` el script

## 4. Documentación

- [x] 4.1 Actualizar `monitoring/README.md`:
  - Reemplazar el Quickstart actual (manual secuencial) por la invocación del orquestador como ruta principal
  - Mantener el flujo manual como sección "uso avanzado / debug"
  - Mencionar las env vars de override
- [x] 4.2 Actualizar `withReplica/README.md` top-level:
  - Mencionar el `Makefile` con targets `up`/`down`/`wait-healthy`
  - Apuntar al orquestador `monitoring/run-comparison.sh` como flujo recomendado
- [x] 4.3 Documentar la **break change** del default de `random_changes.py` en `load-generator/Makefile` (comentario en `run-5.7`/`run-8`) o en un README pequeño en ese dir, según donde quede más visible

## 5. Verificación end-to-end

- [x] 5.1 `make up && make wait-healthy` desde `withReplica/` — confirmar que ambos stacks llegan healthy
- [x] 5.2 Ejecutar el orquestador con defaults: `./monitoring/run-comparison.sh` — debe terminar en ~80s sin intervención y producir `/tmp/comparison.png`
- [x] 5.3 Inspeccionar los CSVs: ambos tienen ≥ 30 muestras (~75 con `-i 1` y drift de docker stats), con valores numéricos durante la ventana de carga
- [x] 5.4 Inspeccionar el PNG: 6 paneles, dos series visibles, el escalón de carga es claramente visible alrededor de t=20–60s
- [x] 5.5 Verificar pre-flight: con un stack apagado (`cd mysql5.7 && docker compose down`), reejecutar el orquestador → debe fallar con exit 2 y mensaje claro
- [x] 5.6 Verificar override: `LOAD_S=10 PRELOAD_S=5 POSTLOAD_S=5 ./monitoring/run-comparison.sh` termina en ~20s
- [x] 5.7 `make down` — confirmar que ambos stacks se limpian
