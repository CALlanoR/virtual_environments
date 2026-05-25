## Why

Hoy la comparación de I/O entre los stacks 5.7 y 8 requiere coordinación manual: levantar dos stacks, arrancar dos monitores con `-d N`, esperar, lanzar dos generadores de carga, esperar, generar el plot. El Quickstart actual del README explica esos pasos en una secuencia "una pasada por stack" precisamente porque el orquestamiento manual con `& wait` es propenso a errores. Pero hacerlo en serie pierde el valor de comparar ambos stacks bajo idéntica carga simultánea.

Necesitamos un **orquestador único** que lance los dos monitores en paralelo, espere un baseline limpio, dispare los dos generadores con duración acotada, deje un cooldown post-load, y genere automáticamente el plot. Y un punto de entrada Makefile en el top-level que simplifique levantar/bajar ambos stacks (sin reemplazar la decisión del usuario de ejecutar el monitoreo a mano).

Para que el orquestador termine limpiamente sin Ctrl+C, el `random_changes.py` debe **auto-pararse tras una duración**. Hoy corre indefinidamente — había `-d` implícito vía Ctrl+C. Lo convertimos en flag explícito `-d N` con default 40s y `-i N` con default 1s (un evento por segundo) para producir señal CDC más densa y comparable en una ventana corta.

## What Changes

- **`load-generator/random_changes.py`**: añadir flags `-i N` (intervalo en segundos, default **1**) y `-d N` (duración total en segundos, default **40**, `0` = infinito). Cuando se alcanza la duración, el script termina con exit 0 sin necesidad de señal externa. La detección de tecla `C` y `Ctrl+C` se mantiene como ruta de salida temprana.
- **BREAKING**: el comportamiento por defecto cambia de "evento cada 10s, hasta Ctrl+C" a "evento cada 1s, durante 40s, luego termina". Los Makefile targets `run-5.7`/`run-8` heredan los nuevos defaults; quien quiera el comportamiento legacy puede pasar `-i 10 -d 0`.
- **`withReplica/Makefile` (nuevo, top-level)**: targets `up`, `down`, `ps`, `wait-healthy`, `help` que operan sobre ambos stacks (`mysql5.7/` y `mysql8/`) en orden. **No** incluye un target para correr el monitoreo — eso queda manual vía el script bash nuevo, por decisión explícita del usuario.
- **`monitoring/run-comparison.sh` (nuevo)**: script bash orquestador. Flujo:
  1. Pre-flight: ambos stacks healthy + venvs creados.
  2. Lanza ambos monitores con `-i 1 -d 80` en background (capturando a `/tmp/mysql57.csv` y `/tmp/mysql8.csv`).
  3. Espera **20s** (baseline pre-load).
  4. Lanza ambos `random_changes.py` con `-i 1 -d 40` en background.
  5. Espera a que ambos generadores terminen (~40s).
  6. Espera **20s** más para que los monitores capturen la fase post-load.
  7. Genera el PNG vía `monitoring/plot/make plot`.
  8. Imprime ruta del PNG y de los CSVs.
- Documentar el nuevo flujo en `monitoring/README.md` y `withReplica/README.md`.

## Capabilities

### New Capabilities
<!-- Sin nuevas capabilities — todo encaja en las dos existentes. -->

### Modified Capabilities
- `mysql-replica-debezium-test`: cambia el comportamiento del generador `random_changes.py` (defaults de intervalo y duración + auto-stop), y añade un Makefile top-level para gestionar el ciclo de vida de ambos stacks.
- `replica-io-monitoring`: añade el orquestador `run-comparison.sh` que coordina monitores + generadores + plot en un solo comando.

## Impact

- **Código modificado**:
  - `load-generator/random_changes.py`: nuevos flags `-i`/`-d`, defaults 1/40, lógica de auto-stop por duración (ya existía la infraestructura del `stop_event`; solo añadir el timer).
  - `load-generator/Makefile`: targets `run-5.7`/`run-8` heredan los defaults nuevos; añadir un comentario explicativo.
- **Código nuevo**:
  - `withReplica/Makefile` (top-level).
  - `monitoring/run-comparison.sh`.
- **Documentación**: actualizar `monitoring/README.md` (Quickstart usa el orquestador) y `withReplica/README.md` (mencionar el Makefile).
- **Sin cambios** en imágenes Docker, configs MySQL/Debezium, ni los stacks `mysql5.7/` y `mysql8/`.
- **Compatibilidad**: el cambio de defaults en `random_changes.py` es una **break change** para quien dependiera del comportamiento "indefinido hasta Ctrl+C". Mitigación: documentado y trivial de revertir con `-d 0 -i 10`.
