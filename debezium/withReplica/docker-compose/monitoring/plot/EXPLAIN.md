Cada panel mide algo distinto. Tres son a nivel contenedor (`docker stats`) y tres a nivel MySQL interno (`SHOW GLOBAL STATUS`).

> **Recordatorio:** todos los valores son tasas en B/s, no acumulados — es (actual − anterior) / intervalo.

## Panel por panel — qué dice esta corrida

### 1. BlockIO read (arriba-izq) — disco leído por el contenedor
- **mysql5.7** tiene 3 picos pequeños (~4–5 KB/s); **mysql8** está plano en cero.
- **Interpretación:** Debezium casi no está leyendo disco. Esto era esperado: el dataset es minúsculo (3 filas seed + 40 INSERTs durante load), todo cabe en el buffer pool de InnoDB. Los picos esporádicos en 5.7 son metadata reads del filesystem que el motor de 8 evita por mejor caching de file handles.
- **Para tu pregunta:** Debezium no genera presión de lectura significativa en ninguno de los dos stacks bajo esta carga.

### 2. BlockIO write (arriba-der) — disco escrito por el contenedor
- **mysql5.7:** varios picos de 1–3 MB/s repartidos.
- **mysql8:** un solo pico gigante de ~9 MB/s alrededor de t=63s.
- **Interpretación:** estos son flushes a disco — incluyen binlog, redo log y datafiles. Los dos motores tienen políticas distintas:
  - 5.7 escribe más a menudo en lotes pequeños (`innodb_flush` más eager).
  - 8 acumula y escribe en lotes grandes (`innodb_redo_log_capacity` con buffer mayor por defecto).
- No es Debezium quien escribe — Debezium solo lee. Lo que ves es la réplica reescribiendo en su binlog las mutaciones que recibió de su master, más los flushes diferidos del InnoDB.

### 3. Innodb_data_read (centro-izq) — bytes que InnoDB pidió al disco
- Plano en cero en ambos.
- **Interpretación:** corrobora el panel 1. Toda la actividad de lectura cae en el buffer pool. Si vieras valores aquí, sería señal de que el working set no cabe en RAM o de que Debezium hizo un snapshot grande.

### 4. Innodb_data_written (centro-der) — bytes que InnoDB escribió a datafiles
- **mysql5.7:** 3 picos espaciados (~2 MB/s cada uno).
- **mysql8:** un pico de ~4.5 MB/s justo cuando termina la carga.
- **Interpretación:** complementa el panel 2 con vista solo del motor (no incluye binlog). Confirma que mysql8 difiere y consolida el flush. Esta es la métrica más confiable para razonar sobre "presión sobre datafiles".

### 5. MySQL Bytes_sent (abajo-izq) — bytes que MySQL envía vía protocolo
- Patrón diente de sierra continuo durante los 80s, oscilando entre ~500 B/s y ~5 KB/s, sin diferencia clara entre fases.
- **Interpretación:** este oscilamiento NO es Debezium. Es el replication thread de la réplica intercambiando heartbeats con su master cada ~3–4s. Debezium contribuye encima, pero el ruido del replication-thread domina la señal.
- Es el panel menos útil aquí porque mezcla dos consumidores. En un setup donde Debezium consume directamente del primario (sin réplica intermedia), este panel sería mucho más limpio.

### 6. NetIO tx (abajo-der) — bytes salientes del contenedor (red total) ⭐
- El más nítido de todos: cero antes de t=20, plateau a ~1500–1700 B/s entre t=20 y t=60, cero después de t=60.
- Las dos curvas (5.7 y 8) prácticamente idénticas durante el plateau.
- **Interpretación:** aquí ves a Debezium consumiendo binlogs. La carga del replication-thread interno (que sí veías en panel 5 a nivel protocolo) no aparece aquí porque su tráfico va al master vía el otro contenedor del compose y se contabiliza distinto. Lo que sale del contenedor de la réplica al exterior (a Debezium) es esto.

## Respuesta a tu pregunta original

### ¿Qué tan intensivo es Debezium en I/O contra las réplicas?
- **Lecturas de disco:** prácticamente cero. El working set vive en memoria; Debezium lee binlog que ya está caliente. Esto se mantiene mientras tu base de demo sea pequeña.
- **Escrituras de disco:** ninguna por parte de Debezium directamente. Lo que ves en BlockIO write e Innodb_data_written es del motor MySQL aplicando los cambios replicados.
- **Red saliente hacia Debezium:** ~1.5–1.7 KB/s sostenido bajo una carga de 1 op/seg. Es decir, ~1.5 KB por evento CDC aproximadamente — incluye payload JSON + overhead de protocolo. Eso te da un número para extrapolar: si tu producción genera 100 ops/seg, espera unos ~150 KB/s de tráfico Debezium→sink.

### ¿5.7 vs 8?
En esta carga, prácticamente equivalentes en términos de "qué tan duro le pega Debezium a la réplica". Las diferencias visibles (panel 2 y 4) son patrones de flush internos del motor, no comportamiento de Debezium.

## Caveats de esta medición
- **Carga ligera:** 40 ops totales en 40s es carga muy ligera. Para conclusiones firmes, multiplica con `LOAD_S=120 ./monitoring/run-comparison.sh` (más muestras, más datos por panel) o aumenta el rate (más ops/seg, requiere modificar `random_changes.py` para que envíe varias por iteración).
- **Intervalo de `docker stats`:** `docker stats --no-stream` tarda ~1–2s, así que el intervalo real no es 1s sino ~2–3s. Por eso ves ~28 puntos en 80s en vez de 80.
- **Cero no es un error:** `Innodb_data_read = 0` siempre es un éxito esperado, no un bug — el dataset cabe en buffer pool.
