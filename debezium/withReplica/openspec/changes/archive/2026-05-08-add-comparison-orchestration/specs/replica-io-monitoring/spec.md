## ADDED Requirements

### Requirement: Orquestador `run-comparison.sh` para captura comparativa automática
El sistema SHALL incluir un script bash `withReplica/monitoring/run-comparison.sh` que, en una sola invocación, capture trazas de I/O de ambos stacks bajo carga sintética idéntica y produzca un PNG comparativo, sin requerir intervención manual durante la ejecución.

El script SHALL ejecutar el siguiente flujo:
1. Pre-flight: verificar que ambos contenedores `mysql-replica` (stack 5.7) y `mysql8-replica` (stack 8) están corriendo, y que existen los venvs en `load-generator/.venv/` y `monitoring/plot/.venv/`. Si algo falta, salir con exit 2 y mensaje accionable.
2. Lanzar ambos monitores (`monitor-mysql5.7.sh` y `monitor-mysql8.sh`) en background, con `-i 1 -d $TOTAL`, redirigiendo a CSVs en `/tmp/`.
3. Esperar `PRELOAD_S` (default **20**) segundos de baseline.
4. Lanzar ambos `random_changes.py` en background con `-i 1 -d $LOAD_S` (default **40**) — uno por stack.
5. Esperar a que ambos generadores terminen (~LOAD_S segundos).
6. Esperar `POSTLOAD_S` (default **20**) segundos adicionales para que los monitores capturen la fase post-load.
7. Esperar a que ambos monitores terminen (terminan solos por su propio `-d`).
8. Invocar `monitoring/plot/plot.py` con los dos CSVs y producir un PNG en `/tmp/comparison.png` (sobreescribible).

El script SHALL aceptar overrides vía variables de entorno: `PRELOAD_S`, `LOAD_S`, `POSTLOAD_S`, `CSV57`, `CSV8`, `OUT`. Una invocación con `--help` o `-h` imprime los defaults.

#### Scenario: Pre-flight detecta stack apagado
- **WHEN** se ejecuta `./monitoring/run-comparison.sh` con uno de los dos stacks no corriendo
- **THEN** el script imprime un mensaje de error que identifica qué contenedor falta y termina con exit 2 antes de empezar la captura

#### Scenario: Pre-flight detecta venv faltante
- **WHEN** se ejecuta el orquestador y `load-generator/.venv/bin/python` o `monitoring/plot/.venv/bin/python` no existen
- **THEN** el script imprime un mensaje sugiriendo `make venv` en el directorio correspondiente y termina con exit 2

#### Scenario: Captura completa con ambos stacks healthy
- **WHEN** se ejecuta `./monitoring/run-comparison.sh` con ambos stacks healthy y los venvs presentes
- **THEN** el script termina con exit 0 después de aproximadamente `PRELOAD_S + LOAD_S + POSTLOAD_S` segundos, habiendo creado `/tmp/mysql57.csv`, `/tmp/mysql8.csv` con muestras de baseline + load + cooldown, y `/tmp/comparison.png` con el plot comparativo

#### Scenario: Overrides por variables de entorno
- **WHEN** se ejecuta `LOAD_S=20 PRELOAD_S=10 POSTLOAD_S=10 ./monitoring/run-comparison.sh`
- **THEN** el script usa esos valores en lugar de los defaults y termina en aproximadamente 40 segundos en lugar de 80

#### Scenario: SIGINT durante la ejecución
- **WHEN** el usuario envía `Ctrl+C` mientras el orquestador está corriendo
- **THEN** el script termina los procesos hijos (monitores y generadores), informa que la captura fue interrumpida y termina con exit code distinto de 0; no intenta generar el plot

#### Scenario: Plot generado tiene contenido visible
- **WHEN** se completa una corrida normal del orquestador
- **THEN** el PNG resultante es un archivo válido > 50KB y muestra series temporales para los seis paneles (BlockIO read/write, Innodb_data_read/written, MySQL Bytes_sent, NetIO tx) con dos curvas etiquetadas `mysql5.7` y `mysql8`
