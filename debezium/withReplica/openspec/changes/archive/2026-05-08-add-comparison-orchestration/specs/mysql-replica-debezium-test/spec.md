## MODIFIED Requirements

### Requirement: Generador de carga sintética en Python con selector de target
El sistema SHALL incluir, bajo `withReplica/load-generator/`, un programa Python 3.12 que se conecte al primario del stack indicado por el flag `--target {mysql5.7,mysql8}` y ejecute operaciones aleatorias sobre `inventory.customers` (`INSERT`, `UPDATE` o `DELETE` elegidas al azar). El programa SHALL aceptar:
- `--interval N` (default **1**): segundos entre operaciones.
- `--duration N` (default **40**): segundos totales de ejecución; al alcanzarlos, el script termina con exit 0 sin necesidad de señales externas. `--duration 0` SHALL significar "infinito" (corre hasta tecla `C`/SIGINT/SIGTERM).
- Mapeo de target: `mysql5.7` → puerto 3306, `mysql8` → puerto 3308. Flags opcionales `--host`/`--port` sobrescriben.

#### Scenario: Selección de target mysql5.7
- **WHEN** se ejecuta `random_changes.py --target mysql5.7` con el stack 5.7 corriendo
- **THEN** las operaciones llegan al primario del stack 5.7 (puerto 3306) y los eventos CDC aparecen en los logs de `cdc-sink` de ese stack

#### Scenario: Selección de target mysql8
- **WHEN** se ejecuta `random_changes.py --target mysql8` con el stack 8 corriendo
- **THEN** las operaciones llegan al primario del stack 8 (puerto 3308) y los eventos CDC aparecen en los logs de `cdc-sink` de ese stack

#### Scenario: Target requerido
- **WHEN** se ejecuta `random_changes.py` sin `--target` ni `--host/--port`
- **THEN** el programa rechaza la ejecución con un mensaje de error indicando que falta el target

#### Scenario: Auto-stop por duración (default)
- **WHEN** se ejecuta `random_changes.py --target mysql5.7` (sin pasar `--duration`)
- **THEN** el script emite aproximadamente 40 operaciones (intervalo default 1s, duración default 40s) y termina solo con exit 0 sin necesidad de Ctrl+C ni tecla C

#### Scenario: Intervalo y duración configurables
- **WHEN** se ejecuta `random_changes.py --target mysql8 -i 2 -d 10`
- **THEN** el script emite aproximadamente 5 operaciones (cada 2s durante 10s) y termina solo con exit 0

#### Scenario: Modo infinito explícito
- **WHEN** se ejecuta `random_changes.py --target mysql5.7 -d 0`
- **THEN** el script corre hasta recibir tecla `C`, SIGINT o SIGTERM, y nunca termina por timeout

#### Scenario: Detención con la tecla C
- **WHEN** el usuario pulsa la tecla `C` (o `c`) mientras el generador corre con stdin conectado a un TTY
- **THEN** el generador detiene el bucle, cierra la conexión a MySQL y termina con exit code 0

#### Scenario: Detención con SIGINT
- **WHEN** el usuario envía `Ctrl+C` (SIGINT) o el script recibe SIGTERM
- **THEN** el generador detiene el bucle, cierra la conexión a MySQL y termina con exit code 0

#### Scenario: Operaciones disparan eventos CDC
- **WHEN** el generador inserta/actualiza/elimina filas en `inventory.customers` con el stack en marcha
- **THEN** los eventos correspondientes (`op=c`, `op=u`, `op=d`) aparecen en los logs de `cdc-sink`

## ADDED Requirements

### Requirement: Makefile top-level para gestionar ambos stacks
El sistema SHALL incluir un `Makefile` en `withReplica/` (top-level) con targets que operen sobre **ambos** stacks (`mysql5.7/` y `mysql8/`) en orden: `up` (levantar), `down` (apagar borrando volúmenes), `ps` (estado), `wait-healthy` (bloquea hasta healthchecks OK) y `help`. El Makefile NO SHALL incluir un target que ejecute el orquestador de monitoreo — la ejecución del monitoreo es manual por decisión explícita del usuario.

#### Scenario: Levantar ambos stacks
- **WHEN** se ejecuta `make up` desde `withReplica/`
- **THEN** ambos stacks (`mysql5.7/` y `mysql8/`) son levantados con `docker compose up -d` y los puertos 3306/3307/3308/3309 quedan publicados al host

#### Scenario: Bajar ambos stacks
- **WHEN** se ejecuta `make down` desde `withReplica/`
- **THEN** ambos stacks son detenidos con `docker compose down -v`, eliminando contenedores, redes y volúmenes anónimos

#### Scenario: Esperar a healthy
- **WHEN** se ejecuta `make wait-healthy` después de un `make up` reciente
- **THEN** el target bloquea hasta que los cuatro contenedores MySQL (`mysql-primary`, `mysql-replica`, `mysql8-primary`, `mysql8-replica`) reportan estado `healthy`, y termina con exit 0

#### Scenario: Estado de ambos stacks
- **WHEN** se ejecuta `make ps`
- **THEN** se imprime el estado (`docker compose ps`) de ambos stacks de forma diferenciada (con encabezados que identifican cada uno)

#### Scenario: El Makefile NO ejecuta el orquestador
- **WHEN** se ejecuta `make help`
- **THEN** la lista de targets NO incluye un target que invoque `monitoring/run-comparison.sh`; en su lugar, la ayuda menciona que el monitoreo se invoca manualmente con ese script
