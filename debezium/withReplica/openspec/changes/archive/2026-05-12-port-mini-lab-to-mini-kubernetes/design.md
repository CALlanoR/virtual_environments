## Context

Hoy el laboratorio CDC vive en `withReplica/docker-compose/` con dos stacks paralelos (`mysql5.7/` y `mysql8/`), cada uno compuesto por cuatro contenedores: `mysql-primary`, `mysql-replica`, `debezium-server`, `cdc-sink` (sidecar HTTP echo). El generador de carga vive aparte en `load-generator/` y se invoca desde el host vía un venv local. La capability [[mysql-replica-debezium-test]] documenta los requisitos de ese laboratorio.

El usuario opera un cluster **minikube** local y quiere ejercitar el mismo escenario sobre primitivas k8s (StatefulSets, Services, ConfigMaps, Secrets, Jobs). El objetivo no es producción: es un mini-laboratorio reproducible que viva al lado del docker-compose, no que lo reemplace.

Constraints relevantes:
- Debezium 3.5 se publica solo en quay.io y la imagen oficial no incluye el conector MySQL → ya existe un `Dockerfile` derivado en `docker-compose/mysql8/debezium/` que lo añade. Se reutiliza esa imagen.
- El stack 5.7 está congelado en Debezium 2.4.2.Final (último que soporta MySQL 5.7) y usa la sintaxis legacy de replicación (`CHANGE MASTER TO`, `log_slave_updates`). El stack 8 usa la moderna (`CHANGE REPLICATION SOURCE TO`, `log_replica_updates`).
- El monitoreo (`docker-compose/monitoring/`) queda **fuera de alcance** por decisión explícita del usuario.

## Goals / Non-Goals

**Goals:**
- Reproducir 1:1 el comportamiento observable de cada stack docker-compose en mini-kubernetes: replicación primary→replica activa, Debezium leyendo binlogs de la réplica, eventos CDC visibles vía `kubectl logs cdc-sink`, filtrado por `table.include.list`.
- Permitir que **ambos stacks coexistan** en el mismo cluster minikube sin colisión (un namespace por stack).
- Permitir que el laboratorio k8s coexista con un docker-compose corriendo en el mismo host (sin chocar puertos host).
- Ofrecer un Makefile con la misma ergonomía que el de docker-compose (`up`, `down`, `ps`, `wait-healthy`, `help`) más targets específicos de k8s/minikube (`image-load`, `load-5.7`, `load-8`).
- Documentar prerrequisitos y comandos en un único `README.md` autocontenido.
- Mantener los archivos de configuración (`my.cnf`, init SQL, `application.properties`) idénticos a los del docker-compose donde sea posible — solo cambiando los hostnames internos al naming k8s.

**Non-Goals:**
- Portar el monitoreo (`monitoring/run-comparison.sh`, `monitoring/plot/`). No se incluye ningún Pod/Job/CronJob de monitoreo en este cambio.
- Producción: nada de TLS, RBAC fino, NetworkPolicies, recursos productivos, multinodo, HA.
- Helm chart / Kustomize overlays: se entregan YAMLs planos para mantener el laboratorio legible. Si más adelante crece, se podrá Kustomize-ar.
- Reescribir el generador de carga: se reutiliza `random_changes.py` tal cual, montado desde un ConfigMap dentro de un Job. Conserva el flag `--target` y los defaults (40s).
- Ingress: no se configura. El acceso externo es vía NodePort + `minikube service`/`kubectl port-forward`.

## Decisions

### D1. Un namespace por stack: `cdc-mysql57` y `cdc-mysql8`

Aislar cada stack en su propio namespace evita choques de nombres de Service (ambos stacks usan `mysql-primary`, `mysql-replica`, `debezium-server`, `cdc-sink`) y permite reusar los `application.properties` sin modificarlos (hostnames internos al namespace son idénticos en ambos).

**Alternativa descartada**: prefijar cada nombre con `mysql8-`/`mysql57-` en el mismo namespace. Funciona pero obliga a tocar `application.properties` (`database.hostname=mysql8-mysql-replica`) y a duplicar archivos. Más fricción que beneficio.

### D2. MySQL como StatefulSet con PVC, no Deployment

MySQL es stateful. Aunque para un laboratorio local podríamos usar `emptyDir`, un StatefulSet con un PVC por instancia da nombres DNS estables (`mysql-primary-0.mysql-primary.cdc-mysql8.svc.cluster.local`) y comportamiento de arranque ordenado. Se usa un Service headless por StatefulSet para el DNS estable + un Service ClusterIP "alias" con el nombre corto (`mysql-primary`, `mysql-replica`) para que `application.properties` siga apuntando a `mysql-replica` literal.

**Alternativa descartada**: Deployment + emptyDir. Más simple pero pierde nombres DNS estables al reiniciar, y no es honesto con el patrón k8s para stateful workloads.

**Trade-off**: requiere que minikube tenga el storage-provisioner activo (lo es por default, addon `storage-provisioner`). El README lo verifica.

### D3. Debezium Server y cdc-sink como Deployment (replicas=1)

Son stateless (los offsets de Debezium se persisten en `/debezium/data` montado como PVC; el sink es puro echo). Deployment es suficiente.

**Persistencia Debezium**: PVC `debezium-data` montado en `/debezium/data`. Necesario para que offsets y schema history sobrevivan a reinicios del Pod (paridad con el volumen `debezium-data` del docker-compose).

### D4. Configuración vía ConfigMap, secretos vía Secret

- **ConfigMaps**:
  - `mysql-primary-config`: `my.cnf`.
  - `mysql-primary-initdb`: scripts `01-users.sql`, `02-demo-schema.sql` montados en `/docker-entrypoint-initdb.d/`.
  - `mysql-replica-config`: `my.cnf` + `healthcheck.sh`.
  - `mysql-replica-initdb`: `01-start-replica.sql`.
  - `debezium-config`: `application.properties` montado en `/debezium/config/` (stack 8) o `/debezium/conf/` (stack 5.7, paths distintos según versión).
  - `load-generator-script`: `random_changes.py` + `requirements.txt`.
- **Secret**: `mysql-credentials` con `MYSQL_ROOT_PASSWORD=root` (lab — no es secreto real, pero usar Secret en lugar de env literal es la forma idiomática).

**Trade-off**: el password está en un Secret no encriptado. Es un laboratorio local; documentado en README. No se entrega un sealed-secrets / external-secrets setup.

### D5. Acceso desde el host vía NodePort en puertos altos disjuntos del docker-compose

Para que el laboratorio k8s no choque con un docker-compose corriendo en paralelo:
- Stack 5.7: NodePort **30306** (primary) y **30307** (replica).
- Stack 8: NodePort **30308** (primary) y **30309** (replica).

El usuario accede con `minikube service mysql-primary -n cdc-mysql8 --url` o `kubectl port-forward -n cdc-mysql8 svc/mysql-primary 3308:3306`. El README muestra ambos.

**Alternativa descartada**: LoadBalancer con `minikube tunnel`. Requiere proceso en background; más fricción para un lab.

### D6. Imagen custom de Debezium 3.5: build local + `minikube image load`

El stack 8 requiere `withreplica/debezium-server-mysql:3.5.0.Final` (imagen derivada con el conector MySQL). El Makefile incluye:

```
make image-build       # docker build -t withreplica/debezium-server-mysql:3.5.0.Final ../docker-compose/mysql8/debezium
make image-load        # minikube image load withreplica/debezium-server-mysql:3.5.0.Final
```

Se reutiliza el Dockerfile existente en `docker-compose/mysql8/debezium/Dockerfile` (no se duplica). Los manifiestos referencian la imagen con `imagePullPolicy: IfNotPresent` para que k8s la encuentre en el daemon de minikube tras `image load`.

**Alternativa descartada**: publicar la imagen en un registry. Innecesario para un lab local; añade fricción.

### D7. Healthcheck de la réplica: liveness/readiness con `exec`

Se reutiliza `healthcheck.sh` montado desde ConfigMap. Se define un `readinessProbe` y `livenessProbe` con `exec: ["/usr/local/bin/replica-healthcheck.sh"]`, mismos thresholds que el docker-compose (período 5s, timeout 10s, 30 retries en initial 60s).

**Detalle**: el script depende de `mysql` CLI presente en la imagen base `mysql:8.0`/`mysql:5.7` — ya lo está, así que no requiere imagen sidecar.

### D8. Init de la réplica: initContainer + script en `/docker-entrypoint-initdb.d/`

MySQL ejecuta scripts en `/docker-entrypoint-initdb.d/` solo durante la inicialización del datadir. Para la réplica, el `01-start-replica.sql` original asume que el primary ya está listo (en docker-compose lo garantiza `depends_on: service_healthy`).

En k8s, el StatefulSet de la réplica se ordena tras el del primary, pero el init script corre durante el bootstrap del datadir — y para entonces el primary podría no haber terminado sus propios init scripts. Solución: un `initContainer` `wait-for-primary` que hace `mysqladmin ping -h mysql-primary -uroot -proot` con retry hasta que responda; solo entonces el container MySQL real arranca y ejecuta `01-start-replica.sql`.

**Alternativa descartada**: poll con sleep en el ENTRYPOINT del propio container. Más frágil y mezcla responsabilidades.

### D9. cdc-sink expuesto solo dentro del namespace

Service ClusterIP `cdc-sink:8080` (no NodePort). Los eventos se observan con `kubectl logs -n cdc-mysql8 deploy/cdc-sink -f`. El usuario no necesita acceso externo al sink; el patrón "ver eventos en stdout" se mantiene.

### D10. load-generator como Job on-demand con `kubectl create job`

El generador se modela como una `Job` con `ttlSecondsAfterFinished: 300` para auto-limpieza. La imagen es `python:3.12-slim`; el script y `requirements.txt` se montan desde ConfigMap; un initContainer hace `pip install -r requirements.txt` en un emptyDir compartido con el container principal (evita rebuild de imagen).

Patrón de invocación: el Makefile lleva un YAML `load-generator-job.yaml` con `target=mysql8` y otro con `target=mysql5.7`. `make load-8` aplica el YAML; cada invocación crea un Job nuevo con sufijo random (`metadata.generateName: load-mysql8-`).

**Alternativa descartada**: imagen custom con dependencias preinstaladas. Más rápida al ejecutar, pero requiere build + image-load. Para 1 dep (PyMySQL), `pip install` al arranque es aceptable (~3s).

El Job target apunta al Service `mysql-primary` del namespace correspondiente. El generador usa `--host mysql-primary --port 3306` desde dentro del cluster (override de los defaults `127.0.0.1:3306/3308`).

### D11. Makefile orquesta ambos stacks + flujo minikube

Targets (paridad con docker-compose donde aplica):
- `help` — listado.
- `image-build` — docker build de la imagen custom de Debezium 3.5.
- `image-load` — `minikube image load`.
- `up` — `kubectl apply -k mysql5.7/` y `mysql8/` (cada stack es una "carpeta de manifiestos"; si crece, se Kustomize-a).
- `up-5.7` / `up-8` — un solo stack.
- `wait-healthy` — espera a que los Pods MySQL estén Ready (usando `kubectl wait --for=condition=ready pod -l app=mysql-replica --timeout=300s`).
- `ps` — `kubectl get all -n cdc-mysql57` y `-n cdc-mysql8`.
- `logs-sink-5.7` / `logs-sink-8` — `kubectl logs -n <ns> deploy/cdc-sink -f`.
- `load-5.7` / `load-8` — `kubectl apply -f load-generator/job-mysql5.7.yaml` / `-f job-mysql8.yaml`.
- `down` — `kubectl delete namespace cdc-mysql57 cdc-mysql8 --ignore-not-found`.

`down` borra namespaces (y con ellos todos los recursos + PVCs). No es destructivo accidental — el usuario lo ejecuta explícitamente.

### D12. Estructura de archivos en `mini-kubernetes/`

```
mini-kubernetes/
├── Makefile
├── README.md
├── mysql5.7/
│   ├── 00-namespace.yaml
│   ├── 01-configmaps.yaml         # mysql-primary-config, mysql-primary-initdb, mysql-replica-config, mysql-replica-initdb, debezium-config
│   ├── 02-secrets.yaml            # mysql-credentials
│   ├── 03-mysql-primary.yaml      # StatefulSet + Service headless + Service alias + Service NodePort
│   ├── 04-mysql-replica.yaml      # StatefulSet (con initContainer wait-for-primary) + Services
│   ├── 05-cdc-sink.yaml           # Deployment + Service ClusterIP
│   └── 06-debezium-server.yaml    # Deployment + PVC debezium-data
├── mysql8/
│   ├── ... (estructura idéntica)
└── load-generator/
    ├── configmap-script.yaml      # random_changes.py + requirements.txt
    ├── job-mysql5.7.yaml          # Job que apunta a cdc-mysql57/mysql-primary
    └── job-mysql8.yaml            # Job que apunta a cdc-mysql8/mysql-primary
```

## Risks / Trade-offs

- **[Riesgo] El init script de la réplica corre antes de que el primary haya replicado sus usuarios** → Mitigación: initContainer `wait-for-primary` con retry y validación adicional `SELECT 1` para confirmar que `repl@'%'` ya existe (se replica como parte de `01-users.sql`). Si la replica se reinicia con datadir existente, el init no se vuelve a correr — es seguro.

- **[Riesgo] PVCs persisten tras `make down` si el namespace no se borra con `--wait`** → Mitigación: el target `down` usa `kubectl delete namespace ... --ignore-not-found --wait=true` (default). En minikube los PVCs se borran limpiamente.

- **[Riesgo] minikube sin recursos** → 4 MySQL + 2 Debezium + 2 sink + ocasional Job. Mitigación: README sugiere `minikube start --cpus=4 --memory=6g` mínimo. Documentar `requests/limits` modestos (256Mi por MySQL, 512Mi Debezium).

- **[Riesgo] El usuario corre el docker-compose y el laboratorio k8s a la vez** → Mitigación: NodePort 30306-30309 en k8s vs. host ports 3306-3309 en docker-compose. Sin colisión.

- **[Riesgo] La imagen custom de Debezium 3.5 no llega al cluster** → Mitigación: el target `up-8` depende de `image-load`; el README documenta `minikube image ls | grep withreplica` como check.

- **[Trade-off] No se modela un sink real (Kafka, http externo)** → mantiene paridad con docker-compose; basta para "ver eventos por consola". Si más adelante se quiere integrar Kafka, se añade en un cambio separado.

- **[Trade-off] YAML plano (no Kustomize/Helm)** → Verbose porque `mysql5.7/` y `mysql8/` son casi iguales. Aceptable para 2 stacks. Si crece, refactor a Kustomize en cambio futuro.

## Migration Plan

No hay migración. Adición pura. Steps de adopción:

1. Construir imagen custom: `make image-build`.
2. Cargar a minikube: `make image-load`.
3. Levantar: `make up` (o un solo stack con `make up-8`).
4. Esperar healthy: `make wait-healthy`.
5. Generar carga: `make load-8`.
6. Observar: `make logs-sink-8`.

**Rollback**: `make down` borra ambos namespaces y todos los recursos. Idempotente.

## Open Questions

- ¿Reusar el mismo `application.properties` literal del docker-compose, o introducir variables `${ENV}` que permitan ajustar `database.hostname` desde k8s? **Decisión preliminar**: reusar literal (los hostnames `mysql-replica` son idénticos porque cada stack vive en su namespace).
- ¿Vale la pena un Service HeadLess separado del Service alias? **Decisión preliminar**: sí — el headless lo necesita el StatefulSet; el alias mantiene paridad con el naming del docker-compose. Coste: 2 Services extra por stack.
