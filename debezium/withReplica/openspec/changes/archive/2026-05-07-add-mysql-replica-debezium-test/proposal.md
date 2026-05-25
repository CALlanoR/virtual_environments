## Why

Aún no existe en este directorio un escenario de prueba que valide cómo Debezium Server captura cambios desde una réplica MySQL en lugar de hacerlo directamente desde el primario. Este patrón es común en producción para descargar al primario de la lectura de binlogs y validar que los CDC events siguen llegando consistentes desde la réplica. Necesitamos un entorno reproducible (Docker + docker-compose) que permita demostrar y experimentar con este flujo, mostrando los cambios en consola para inspección rápida.

Adicionalmente queremos poder **comparar** el comportamiento entre MySQL 5.7 (con sintaxis legacy y Debezium 2.4.2.Final, última versión soportada para 5.7) y MySQL 8.0 (con sintaxis moderna `CHANGE REPLICATION SOURCE TO` / `START REPLICA` y Debezium 3.5.0.Final), ejecutando ambos stacks en paralelo y reutilizando el mismo generador de carga.

## What Changes

- Reorganizar el directorio en **dos stacks paralelos**, uno por versión mayor de MySQL, cada uno con su propio `docker-compose.yml`:
  - `withReplica/mysql5.7/` — stack actual (MySQL 5.7 + Debezium Server 2.4.2.Final desde Docker Hub, con sink `http` hacia `cdc-sink`). Sintaxis legacy: `CHANGE MASTER TO`, `START SLAVE`, `log_slave_updates`.
  - `withReplica/mysql8/` — stack nuevo (MySQL 8.0 + Debezium Server 3.5.0.Final **desde `quay.io/debezium/server`**, también con sink `http` hacia `cdc-sink` para mantener paridad de observabilidad). Sintaxis moderna: `CHANGE REPLICATION SOURCE TO`, `START REPLICA`, `log_replica_updates`.
- Cada stack orquesta cuatro servicios: `mysql-primary`, `mysql-replica`, `debezium-server`, `cdc-sink`. Los puertos host de los dos stacks son disjuntos (5.7→3306/3307, 8→3308/3309) para que puedan ejecutarse simultáneamente.
- Incluir scripts SQL de inicialización para:
  - Crear el usuario de replicación y arrancar `START SLAVE` en la réplica (sintaxis MySQL 5.7).
  - Crear el usuario y permisos requeridos por Debezium (`REPLICATION SLAVE`, `REPLICATION CLIENT`, `SELECT`, `RELOAD`).
  - Crear una base de datos de demo y al menos una tabla con datos seed para generar eventos.
- Proveer configuración de Debezium Server (`application.properties`) con el conector MySQL apuntando a la réplica, una lista explícita de tablas de interés (`table.include.list`) y un sink de consola.
- Documentar en un `README.md` cómo levantar el stack, generar cambios (INSERT/UPDATE/DELETE) en el primario y observar los eventos CDC en los logs de Debezium.
- Incluir un **generador de carga sintética en Python 3.12** (`load-generator/`) que se conecte al primario del stack elegido (`--target {mysql5.7,mysql8}`) y ejecute operaciones aleatorias (INSERT/UPDATE/DELETE) sobre `inventory.customers` cada 10 segundos hasta que el usuario pulse la tecla **C** o envíe `Ctrl+C`. Acompañado de un `Makefile` con targets para crear (`venv`) y eliminar (`venv-clean`) el entorno virtual y para ejecutar contra cada stack (`run-5.7`, `run-8`).

## Capabilities

### New Capabilities
- `mysql-replica-debezium-test`: escenario(s) contenido(s) en Docker que monta(n) MySQL primario + réplica con replicación activa y un Debezium Server que consume binlogs de la réplica y emite los eventos CDC a consola. Esta capability cubre **dos variantes paralelas** (`mysql5.7/` y `mysql8/`) que comparten el mismo modelo de dominio (base `inventory`, tablas `customers` y `audit_log`) y un generador de carga común con selector de target.

### Modified Capabilities
<!-- N/A: no hay specs previos en openspec/specs/ que cambien. -->

## Impact

- Código nuevo bajo `withReplica/`:
  - `mysql5.7/` con `docker-compose.yml`, `mysql/{primary,replica}/...`, `debezium/conf/application.properties`.
  - `mysql8/` con `docker-compose.yml`, `mysql/{primary,replica}/...`, `debezium/conf/application.properties`.
  - `load-generator/` con `random_changes.py`, `requirements.txt`, `Makefile` (target selector).
  - `README.md` top-level documentando ambos stacks y cómo cambiar de uno a otro.
- Sin cambios en código existente del repositorio fuera de `withReplica/`; se trata de un escenario aislado de pruebas.
- Dependencias externas (imágenes Docker):
  - `mysql:5.7` + `debezium/server:2.4.2.Final` (Docker Hub) para el stack 5.7.
  - `mysql:8.0` + `quay.io/debezium/server:3.5.0.Final` para el stack 8. **Importante**: las imágenes de Debezium 3.x se publican en `quay.io`, no en Docker Hub (el repo `docker.io/debezium/server` no se actualiza desde 2024-10-17 / `3.0.0.Final`).
  - `mendhak/http-https-echo:40` (compartido conceptualmente; cada stack tiene su propio contenedor).
- Dependencias externas (Python): `PyMySQL` para el generador. Requiere `python3.12` instalado localmente.
- Puertos host requeridos disjuntos: stack 5.7 usa **3306/3307**, stack 8 usa **3308/3309**.
- Requiere puertos locales libres para `mysql-primary` (3306), `mysql-replica` (3307) y opcionalmente `debezium-server` (8080 health). Se documentará cómo cambiarlos.
- No introduce dependencias en lenguajes de programación; todo el flujo se ejecuta dentro de contenedores.
