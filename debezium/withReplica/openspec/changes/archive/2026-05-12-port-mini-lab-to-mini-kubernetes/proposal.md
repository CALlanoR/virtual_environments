## Why

El mini-laboratorio de Debezium contra réplicas MySQL ya existe en `withReplica/docker-compose/` y funciona, pero la organización local del usuario incluye un cluster mini-kubernetes (minikube) en el que se prefieren validar los escenarios CDC para ejercitar primitivas k8s reales (StatefulSets, ConfigMaps, Services, Jobs). Reproducir el laboratorio en minikube permite practicar el patrón "Debezium leyendo binlogs de la réplica" sobre objetos nativos de Kubernetes sin depender de docker-compose ni de runners externos.

## What Changes

- Se crea un nuevo directorio `withReplica/mini-kubernetes/` con manifiestos YAML que orquestan **ambos stacks** (mysql5.7 + mysql8) en namespaces separados, replicando 1:1 la topología del docker-compose.
- Cada stack se modela con: dos StatefulSets para MySQL (primary, replica), un Deployment para Debezium Server, un Deployment para `cdc-sink` (sidecar `mendhak/http-https-echo`), ConfigMaps para `my.cnf`/init SQL/`application.properties`, Secrets para passwords, Services internos para la red CDC y Services NodePort para exponer al host los puertos de MySQL.
- El `load-generator` se ejecuta dentro del cluster como un **Job on-demand**: una imagen de Python 3.12 que monta el script `random_changes.py` desde un ConfigMap y se invoca con `make load-5.7` / `make load-8`. Termina solo tras 40s (default) y es repetible.
- Se publica un `Makefile` top-level en `mini-kubernetes/` con targets equivalentes a los del docker-compose (`up`, `down`, `ps`, `wait-healthy`, `load-5.7`, `load-8`, `logs-sink-5.7`, `logs-sink-8`, `help`), pensados para **minikube**: incluyen `image-load` para la imagen custom de Debezium 3.5 que añade el conector MySQL (la misma que ya existe en `docker-compose/mysql8/debezium/`).
- Se incluye un `README.md` con: prerrequisitos (minikube, kubectl, addons habilitados), comandos de arranque, cómo observar eventos en `cdc-sink` (`kubectl logs -f`), cómo conectarse al primary vía NodePort, cómo correr el generador de carga, y limpieza.
- **No incluido (decisión explícita del usuario)**: los scripts y manifiestos del directorio `monitoring/` del docker-compose **NO** se portan. El monitoreo queda como trabajo futuro fuera del alcance de este cambio.
- **No-goals**: no se modifica nada del directorio `docker-compose/`. Es una adición paralela; ambas implementaciones coexisten.

## Capabilities

### New Capabilities
- `mysql-replica-debezium-k8s`: laboratorio mini-kubernetes para CDC con Debezium Server consumiendo binlogs de una réplica MySQL, en dos variantes (mysql5.7 + Debezium 2.4 y mysql8 + Debezium 3.5), con load-generator on-demand como Job. Refleja en k8s nativo el comportamiento que [[mysql-replica-debezium-test]] establece para docker-compose.

### Modified Capabilities
<!-- Ninguna. La capability existente `mysql-replica-debezium-test` describe el laboratorio en docker-compose y permanece sin cambios. La capability `replica-io-monitoring` queda fuera de alcance. -->

## Impact

- **Código nuevo (solo aditivo)**: `withReplica/mini-kubernetes/` con subdirectorios `mysql5.7/`, `mysql8/`, `load-generator/`, más un `Makefile` y `README.md` top-level.
- **Imágenes**: reutiliza las imágenes públicas usadas hoy (`mysql:5.7`, `mysql:8.0`, `debezium/server:2.4.2.Final`, `mendhak/http-https-echo:40`) y la imagen custom `withreplica/debezium-server-mysql:3.5.0.Final` construida con el Dockerfile existente en `docker-compose/mysql8/debezium/Dockerfile`. El Makefile la construye y la carga al daemon de minikube con `minikube image load`.
- **Configuración compartida con docker-compose**: los archivos `my.cnf`, scripts `init/*.sql`, healthcheck de la réplica y `application.properties` se replican como ConfigMaps. Las semánticas (server-id, GTID, `log_slave_updates`/`log_replica_updates`, filtros de tablas Debezium) se mantienen idénticas a las del docker-compose.
- **Puertos host vía NodePort**: para no chocar con un docker-compose corriendo en paralelo, los NodePort usan rangos distintos (ej. 30306/30307/30308/30309). El README explica cómo acceder con `minikube service` o `kubectl port-forward`.
- **Dependencias externas**: minikube, kubectl, GNU make. El usuario ya tiene minikube instalado. Acceso a `quay.io` y `docker.io` desde la red local para tirar imágenes.
- **Sin cambios** en: `docker-compose/`, `openspec/specs/mysql-replica-debezium-test/spec.md`, `openspec/specs/replica-io-monitoring/spec.md`.
