# withReplica — Debezium Server contra réplicas MySQL

Escenario(s) local(es) para experimentar con **Debezium Server consumiendo binlogs de una réplica MySQL** (no del primario), con eventos CDC observables por consola. Hay **dos stacks paralelos** que pueden ejecutarse simultáneamente:

| Stack | MySQL | Debezium Server | Imagen Debezium | Sintaxis | Puertos host |
| --- | --- | --- | --- | --- | --- |
| [`mysql5.7/`](./mysql5.7/README.md) | 5.7 | `2.4.2.Final` | `debezium/server:2.4.2.Final` (Docker Hub) | legacy: `CHANGE MASTER TO`, `START SLAVE`, `log_slave_updates` | primary 3306, replica 3307 |
| [`mysql8/`](./mysql8/README.md)     | 8.0 | `3.5.0.Final` | `quay.io/debezium/server:3.5.0.Final` (**quay.io**, no Docker Hub — el repo de Docker Hub no se actualiza desde 2024-10) | moderna: `CHANGE REPLICATION SOURCE TO`, `START REPLICA`, `log_replica_updates` | primary 3308, replica 3309 |

Ambos stacks comparten:
- Mismo modelo de datos (base `inventory`, tabla `customers` capturada y `audit_log` como control negativo del filtrado).
- Mismo sink de observabilidad (`mendhak/http-https-echo` recibe POSTs y los imprime en su stdout).
- El **mismo generador de carga** en `load-generator/` (Python 3.12 + PyMySQL) con flag `--target {mysql5.7,mysql8}`.

## Cómo operar (Makefile top-level)

Hay un `Makefile` en este directorio que opera sobre **ambos stacks** a la vez:

```bash
make up            # levanta mysql5.7 + mysql8
make wait-healthy  # bloquea hasta que los 4 contenedores MySQL estén healthy
make all           # equivale a 'up && wait-healthy'
make ps            # estado de ambos
make down          # apaga ambos (con -v, borra volúmenes)
make help          # listado de targets
```

El Makefile **no** incluye un target para correr el monitoreo — esa parte es manual:

```bash
./monitoring/run-comparison.sh    # 80s, produce /tmp/comparison.png
```

Para más detalle sobre el monitoreo: [`monitoring/README.md`](./monitoring/README.md).

## Cómo trabajar con un solo stack

Si quieres operar un stack solo (sin tocar el otro):

```bash
# Stack 5.7
cd mysql5.7
docker compose up -d
docker compose logs -f cdc-sink   # eventos CDC

# En otra terminal, generar carga (40s default):
cd ../load-generator
make venv          # primera vez
make run-5.7       # corre 40s y termina solo; presiona C para parar antes
```

Para el stack 8 reemplaza `mysql5.7` por `mysql8` y `run-5.7` por `run-8`. Puedes tener ambos arriba a la vez (los puertos son disjuntos).

## Limpieza

Desde el top-level: `make down`.

O por stack:

```bash
cd mysql5.7 && docker compose down -v
cd mysql8   && docker compose down -v
```

## Documentación detallada

- [`mysql5.7/README.md`](./mysql5.7/README.md) — guía específica del stack legacy.
- [`mysql8/README.md`](./mysql8/README.md) — guía específica del stack moderno.
- [`load-generator/README.md`](./load-generator/) (en el `Makefile` con `make help`) — cómo invocar el generador.
- [`monitoring/README.md`](./monitoring/README.md) — scripts bash para monitorear I/O de cada réplica + script Python para visualizar las trazas.

## Por qué dos stacks

Debezium 2.5+ desupportó MySQL 5.7. Por eso:
- Para 5.7 usamos Debezium 2.4.2.Final (último que lo soporta), que **no incluye** el sink `log` (añadido después). Por eso el stack 5.7 usa un sidecar `cdc-sink` con sink `http`.
- Para 8.0 usamos Debezium 3.5.0.Final (estable más reciente). Mantenemos el mismo sidecar `cdc-sink` para que la observabilidad sea idéntica entre los dos stacks y se puedan comparar 1:1.
