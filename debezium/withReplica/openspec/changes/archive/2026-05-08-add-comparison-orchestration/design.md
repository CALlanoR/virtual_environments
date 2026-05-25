## Context

Tras el change anterior `add-replica-io-monitoring`, tenemos los componentes individuales: monitor bash por stack, plot Python, generador de carga. La pregunta natural — *"¿cuál stack es más intensivo en I/O bajo la misma carga?"* — sigue requiriendo varios comandos manuales y un Quickstart en serie. Este change agrega un único orquestador que produce la respuesta en ~80 segundos sin Ctrl+C.

El usuario también pidió un Makefile top-level para subir ambos stacks de forma uniforme, **excluyendo explícitamente** el orquestador del Makefile (lo correrá a mano).

## Goals / Non-Goals

**Goals:**
- Comando único (`./monitoring/run-comparison.sh`) que produce CSVs y PNG comparativo.
- `random_changes.py` se autotermina tras un intervalo configurable, sin requerir señales externas.
- Makefile top-level para `up`/`down`/`ps`/`wait-healthy` ambos stacks.
- Failures rápidos y claros: si los stacks no están up, si los venvs no existen, si los puertos están ocupados → mensaje específico y exit ≠ 0 antes de gastar 80 segundos.

**Non-Goals:**
- El orquestador NO levanta/baja los stacks. El usuario hace eso manualmente con `make up`/`make down`.
- El orquestador NO instala los venvs. Si faltan, falla con un mensaje pidiendo `make venv`.
- Soporte para más de dos stacks o configuraciones paramétricas (e.g., distintas duraciones por stack). Todo el flujo está cableado a 20+40+20=80s. Si el usuario quiere otra duración, puede modificar el script o pasar overrides vía variables de entorno (decisión menor en D5).
- El Makefile top-level NO tiene target para el orquestador — pedido explícito del usuario ("La ejecución del monitoreo será manual").

## Decisions

### D1: Cambio de defaults en `random_changes.py`

- Default actual: `INTERVAL_SECONDS = 10`, sin duración (corre hasta Ctrl+C).
- Nuevo: `--interval 1` y `--duration 40` por defecto. `--duration 0` = infinito (mantener vía explícito).
- **Break change**: cualquiera que ejecute `random_changes.py --target X` sin flags ahora ve un comportamiento distinto. Lo documentamos.
- Auto-stop: después de cada operación, si el tiempo transcurrido ≥ duration, salir limpiamente. La infraestructura de `stop_event` ya existe; solo se le añade un timer.
- Alternativa considerada: dejar los defaults legacy (10s/infinito) y forzar a pasar `-i 1 -d 40` en el orquestador. Descartada — los defaults nuevos son más útiles para el caso "demo CDC contra una réplica" y el orquestador queda más limpio.

### D2: Orquestador `run-comparison.sh`

- Ubicación: `monitoring/run-comparison.sh` (junto a los demás scripts del flujo de monitoreo).
- Estructura del flujo (todos en background con PID guardado):
  ```
  t=0   : spawn monitor-mysql5.7.sh -i 1 -d 80 → /tmp/mysql57.csv
          spawn monitor-mysql8.sh   -i 1 -d 80 → /tmp/mysql8.csv
  t=20  : spawn random_changes.py --target mysql5.7 -i 1 -d 40
          spawn random_changes.py --target mysql8   -i 1 -d 40
  t=60  : ambos random_changes.py terminan solos
  t=80  : ambos monitores terminan solos
  t=80+ : invocar plot.py con los dos CSVs → PNG
  ```
- Variables sobreescribibles (D5):
  - `PRELOAD_S` (default 20)
  - `LOAD_S` (default 40)
  - `POSTLOAD_S` (default 20)
  - `CSV57`, `CSV8`, `OUT` (paths de output)
  - `INTERVAL_MONITOR` (default 1)
- Pre-flight checks (todos antes de empezar el reloj):
  - Contenedores `mysql-replica` y `mysql8-replica` existen y están `Running` (reusa la lógica del `check_container` de `_common.sh`).
  - `load-generator/.venv/bin/python` existe (requiere `make venv` en `load-generator`).
  - `monitoring/plot/.venv/bin/python` existe (requiere `make venv` en `plot/`).
  - Si falta cualquiera: exit 2 con mensaje accionable.
- Manejo de señales: trap SIGINT/SIGTERM que mata todos los procesos hijos (load gens y monitores) y aborta el plot. Importante: el orquestador puede dejar contenedores en ejecución; explícito en el README.
- Pipeo a `tee` para que el usuario vea progreso en tiempo real (cada CSV se escribe en disco mientras se captura, no al final).

### D3: Makefile top-level

- Ubicación: `withReplica/Makefile`.
- Targets:
  - `up` — `cd mysql5.7 && docker compose up -d` y luego mismo para `mysql8/`.
  - `down` — `docker compose down -v` para ambos. **Borra volúmenes** intencionalmente (consistente con el resto del repo: stacks efímeros).
  - `ps` — estado de ambos.
  - `wait-healthy` — bloquea hasta que los healthchecks de los cuatro contenedores MySQL estén `healthy`.
  - `help` — listado de targets.
- **Excluye** un target `run-comparison` o equivalente. Decisión explícita del usuario.
- Alternativa considerada: usar `docker compose --project-directory mysql5.7 --project-directory mysql8`. Descartado: compose v2 no acepta múltiples `--project-directory` simultáneos. La iteración con `cd` por stack es más simple.

### D4: Por qué `-i 1` en el monitor durante el comparison

- Con `-i 5` (default), 80s de captura producen ~16 muestras. Insuficiente para ver la transición pre/load/post nítidamente.
- Con `-i 1`, 80s producen ~50-70 muestras (con drift por overhead de `docker stats`). Resolución fina suficiente para ver claramente el escalón de carga a t=20s y la caída a t=60s.
- Trade-off: el overhead de `docker stats --no-stream` (~1-2s) hace que el intervalo real sea 2-3s, no 1. Aceptable para este caso de uso. Documentado.

### D5: Overrides vía variables de entorno

Por simplicidad y para no añadir argparse a un script bash, los overrides son env vars opcionales:

```bash
PRELOAD_S=10 LOAD_S=60 POSTLOAD_S=10 ./monitoring/run-comparison.sh
```

Defaults exhibidos en el `--help` del propio script.

Alternativa considerada: parseo CLI con `getopts`. Descartado para mantener el script corto; las env vars cubren todos los casos esperados.

### D6: Ubicación del PNG resultante

Default: `/tmp/comparison.png`. Sobreescribible vía `OUT=...`. Por qué `/tmp/` y no CWD: consistencia con el Quickstart existente que ya usa `/tmp/mysql57.csv` y `/tmp/mysql8.csv`. Para análisis persistente, el usuario puede `cp` o pasar otra ruta.

## Risks / Trade-offs

- **Riesgo**: el `random_changes.py` con `-i 1` puede saturar la base si la carga del host es alta. → **Mitigación**: el script reusa la conexión y solo hace 1 query por iteración. ~40 ops por stack en 40s no es carga real para MySQL. Documentado.
- **Riesgo**: el orquestador deja procesos en background si recibe SIGKILL (no atrapable). → **Mitigación**: trap de SIGINT/SIGTERM cubre los casos comunes; SIGKILL queda fuera de alcance, y el usuario puede limpiar con `pkill -f monitor-mysql` y `pkill -f random_changes`.
- **Riesgo**: en máquinas lentas, los `docker stats` con `-i 1` pueden drift hasta 3s reales, comprometiendo la sincronía pre/load/post. → **Mitigación**: el orquestador usa **timestamps absolutos** vía `sleep` en wallclock, no cuenta iteraciones; las fases del orquestador son robustas al drift del monitor.
- **Trade-off**: el cambio de default en `random_changes.py` rompe scripts/aliases existentes que llaman al script sin flags y esperan el comportamiento legacy. Aceptable porque el repo es local de pruebas y el cambio está documentado en proposal/README.

## Migration Plan

Para usuarios del flujo anterior:
- Si tenían un alias `random_changes.py --target X` corriendo indefinidamente, ahora termina en 40s. Para volver al comportamiento legacy: `random_changes.py --target X -i 10 -d 0`.
- El Quickstart manual del README anterior sigue funcionando, pero queda subordinado al nuevo flujo orquestado. Mantener ambos en el README.

## Open Questions

- ¿El orquestador debe también verificar el estado de Debezium Server (que esté procesando eventos), o asume que si el contenedor está up, está bien? → Decisión propuesta: NO. Verificar Debezium agregaría complejidad (parsear logs, llamar HTTP, etc.); confiar en `depends_on: condition: service_healthy` del compose es suficiente.
- ¿Persistir los CSVs por timestamp para no sobrescribir entre runs? → Decisión propuesta: NO por defecto. El usuario puede pasar `CSV57=/tmp/run1-57.csv` etc. si quiere persistir.
