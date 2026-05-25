## ADDED Requirements

### Requirement: Un script de monitoreo por stack
El sistema SHALL incluir, bajo `withReplica/monitoring/`, dos scripts bash ejecutables — `monitor-mysql5.7.sh` y `monitor-mysql8.sh` — uno por stack. Cada script SHALL apuntar al contenedor `mysql-replica` y al puerto host de su stack correspondiente.

#### Scenario: Existencia y permisos de los scripts
- **WHEN** se inspecciona `withReplica/monitoring/`
- **THEN** existen los archivos `monitor-mysql5.7.sh` y `monitor-mysql8.sh`, ambos con el bit de ejecución activo y shebang `#!/usr/bin/env bash`

#### Scenario: Cada script apunta a su stack
- **WHEN** se inspecciona `monitor-mysql5.7.sh`
- **THEN** el script referencia el contenedor de la réplica del stack 5.7 y el puerto host 3307; análogamente, `monitor-mysql8.sh` referencia el de mysql8 y el puerto 3309

### Requirement: Recolección periódica de métricas de contenedor
Cada script SHALL recolectar, en cada iteración, métricas a nivel de contenedor del replica MySQL usando `docker stats --no-stream`: bytes leídos/escritos a bloque (BlockIO), bytes entrantes/salientes de red (NetIO), CPU% y memoria.

#### Scenario: Cada muestra incluye métricas de contenedor
- **WHEN** el script corre durante varios intervalos
- **THEN** cada línea de salida (excepto baseline) contiene los valores actuales de BlockIO read, BlockIO write, NetIO rx, NetIO tx, CPU% y MemUsage del contenedor de la réplica

#### Scenario: Contenedor inexistente
- **WHEN** el script se ejecuta y el contenedor objetivo NO existe (stack apagado)
- **THEN** el script imprime un mensaje de error claro indicando el nombre del contenedor faltante y termina con exit code distinto de 0

### Requirement: Recolección periódica de métricas internas de MySQL
Cada script SHALL consultar `SHOW GLOBAL STATUS` contra la réplica en cada iteración y capturar al menos: `Innodb_data_read`, `Innodb_data_written`, `Bytes_sent`, `Bytes_received`, `Binlog_cache_use`, `Binlog_cache_disk_use`. Los valores reportados al usuario SHALL ser **deltas entre iteraciones**, no acumulados desde el inicio del servidor.

#### Scenario: Primera muestra marcada como baseline
- **WHEN** el script ejecuta su primera iteración
- **THEN** la línea correspondiente reporta los valores MySQL como `baseline` (o equivalente claro), porque aún no hay punto de comparación para calcular delta

#### Scenario: Muestras subsecuentes reportan delta
- **WHEN** el script lleva al menos dos iteraciones completas
- **THEN** los valores MySQL reportados son la diferencia entre la iteración actual y la anterior, divididos por el intervalo (en bytes/seg para tasas de I/O)

#### Scenario: Fallo transitorio de MySQL no aborta el bucle
- **WHEN** la consulta `SHOW GLOBAL STATUS` falla en una iteración (timeout, contenedor no responde momentáneamente)
- **THEN** el script registra el fallo en stderr, marca esa muestra con valores MySQL en `?` y continúa con la siguiente iteración

### Requirement: Modos de salida humano y CSV
Cada script SHALL emitir las muestras por stdout. SHALL soportar dos modos:
- Por defecto: formato **legible para humanos** con columnas alineadas, sufijos de unidades (KB/MB), y header repetido cada N filas.
- Con flag `--csv`: formato **CSV** con un único header en la primera línea y valores en bytes (sin sufijos), apto para `tee` a archivo y análisis posterior.

#### Scenario: Salida por defecto es legible
- **WHEN** se ejecuta el script sin `--csv`
- **THEN** la salida tiene columnas alineadas, sufijos de tamaño (`K`, `M`) y al menos un header inicial con los nombres de las columnas

#### Scenario: Salida CSV es parseable
- **WHEN** se ejecuta el script con `--csv`
- **THEN** la primera línea es un header CSV (campos separados por coma, sin espacios extra) y todas las líneas siguientes son filas de datos coherentes con ese header

### Requirement: Configuración de intervalo y duración
Cada script SHALL aceptar `-i N` (intervalo entre muestras en segundos, default 5) y `-d N` (duración total en segundos; si se omite, corre hasta `Ctrl+C`).

#### Scenario: Intervalo configurable
- **WHEN** se ejecuta el script con `-i 2`
- **THEN** las muestras se producen aproximadamente cada 2 segundos

#### Scenario: Duración limitada
- **WHEN** se ejecuta el script con `-d 30 -i 5`
- **THEN** el script termina solo (exit 0) después de aproximadamente 30 segundos, habiendo producido del orden de 6 muestras

#### Scenario: Sin duración, termina con Ctrl+C
- **WHEN** el script corre sin `-d` y el usuario envía `SIGINT`
- **THEN** el script imprime una línea final de cierre (resumen breve) y termina con exit 0

### Requirement: Visualización offline con script Python
El sistema SHALL incluir, bajo `withReplica/monitoring/plot/`, un script Python (`plot.py`) que tome **uno o dos** CSVs producidos por los scripts bash y genere un archivo PNG con un grid de paneles que muestren las series temporales relevantes (BlockIO read/write, NetIO tx, `Innodb_data_read/written`, `Bytes_sent`, CPU%). El script SHALL alinear las series por tiempo relativo desde la primera muestra de cada CSV.

#### Scenario: Generar reporte de un solo stack
- **WHEN** se ejecuta `plot.py path/to/mysql5.7.csv -o report.png` con un CSV válido
- **THEN** se crea `report.png` con paneles para cada métrica y una sola serie etiquetada `mysql5.7`

#### Scenario: Comparación 5.7 vs 8
- **WHEN** se ejecuta `plot.py mysql5.7.csv mysql8.csv -o compare.png`
- **THEN** se crea `compare.png` con los mismos paneles, cada uno mostrando dos series superpuestas (etiquetadas `mysql5.7` y `mysql8`), alineadas por tiempo relativo desde t=0 de cada CSV

#### Scenario: Suavizado opcional
- **WHEN** se ejecuta el script con `--smooth N` y N>1
- **THEN** las series mostradas son una rolling mean de tamaño N, reduciendo el ruido de muestras a intervalos cortos

#### Scenario: CSV inválido o vacío
- **WHEN** el CSV pasado no existe, está vacío, o no tiene el header esperado
- **THEN** el script termina con exit code distinto de 0 e imprime un mensaje claro indicando qué CSV falló y por qué

### Requirement: Makefile gestiona venv y ejecución del plot
El sistema SHALL incluir un `Makefile` en `withReplica/monitoring/plot/` con targets para crear (`venv`) y eliminar (`venv-clean`) un entorno virtual con `pandas` y `matplotlib`, y un target `plot` que invoque `plot.py` con los CSVs pasados como variable.

#### Scenario: Crear el venv del plot
- **WHEN** se ejecuta `make venv` desde `withReplica/monitoring/plot/` con `python3.12` disponible
- **THEN** se crea `.venv/` con `pandas` y `matplotlib` instalados, sin afectar al venv de `load-generator/`

#### Scenario: Eliminar el venv del plot
- **WHEN** se ejecuta `make venv-clean`
- **THEN** el directorio `.venv/` de `monitoring/plot/` se elimina (idempotente)

#### Scenario: Generar plot vía Makefile
- **WHEN** se ejecuta `make plot CSVS="../mysql5.7.csv ../mysql8.csv"`
- **THEN** el target invoca `plot.py` con esos CSVs y produce el PNG de salida

### Requirement: Documentación
El sistema SHALL incluir `withReplica/monitoring/README.md` que explique cómo correr cada script bash junto al `load-generator` para producir trazas comparables entre los dos stacks, cómo interpretar las métricas reportadas (qué significa cada columna, qué valores son `baseline`, qué diferencia hay entre BlockIO y `Innodb_data_*`), y cómo generar el reporte visual con `plot/`.

#### Scenario: README cubre el flujo recomendado
- **WHEN** un usuario lee `withReplica/monitoring/README.md`
- **THEN** encuentra: comando para ejecutar cada script con `--csv`, ejemplo de combinación con `make run-5.7` / `make run-8`, descripción de cada columna de salida, nota sobre cómo interpretar `BlockIO` vs `Innodb_data_*`, y un ejemplo end-to-end de capturar dos CSVs y generar un PNG comparativo con `plot/`
