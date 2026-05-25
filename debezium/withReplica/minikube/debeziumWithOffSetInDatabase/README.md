# mini-kubernetes — Debezium Server contra réplicas MySQL en minikube

Variante mini-kubernetes del laboratorio que vive en [`../../docker-compose/`](../../docker-compose/README.md). Reproduce 1:1 los dos stacks (`mysql5.7` + `mysql8`) sobre primitivas k8s (StatefulSets, Services, ConfigMaps, Jobs) en namespaces separados.

| Stack | Namespace | MySQL | Debezium Server | NodePort primary / replica |
| --- | --- | --- | --- | --- |
| 5.7 | `cdc-lab` | 5.7 | `debezium/server:2.4.2.Final` (Docker Hub) | **30406** / **30407** |
| 8.0 | `cdc-lab` | 8.0 | `withreplica/debezium-server-mysql:3.5.0.Final` (build local sobre quay.io) | **30408** / **30409** |

Adicionalmente, el MySQL compartido que almacena el estado de Debezium (offsets + schema history para ambos stacks) está expuesto en NodePort **30410** (ver [Acceso desde el host](#acceso-desde-el-host)).

> **El monitoreo no está incluido.** Lo que existe en `../../docker-compose/monitoring/` (scripts bash + script Python para graficar) queda fuera del alcance de esta variante. Puede añadirse en un cambio futuro.

## Topología

```
┌───────────────────────────────  namespace cdc-mysql8  ───────────────────────────────┐
│                                                                                      │
│  ┌──────────────────┐  replicación   ┌──────────────────┐  binlog   ┌──────────────┐ │
│  │ mysql-primary-0  │ ─────────────▶ │ mysql-replica-0  │ ─────────▶│ debezium-... │ │
│  │ (StatefulSet)    │   (GTID, ROW)  │ (StatefulSet)    │           │ (Deployment) │ │
│  └──────────────────┘                └──────────────────┘           └──────┬───────┘ │
│        ▲ NodePort 30308                  NodePort 30309                    │ HTTP    │
│        │                                                                   ▼ POST    │
│   tu cliente / Job                                                ┌────────────────┐ │
│                                                                   │   cdc-sink     │ │
│                                                                   │ (Deployment)   │ │
│                                                                   └────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────┘

(El namespace cdc-mysql57 es estructuralmente idéntico con NodePorts 30306/30307 y Debezium 2.4.2.Final.)
```

## Prerrequisitos

- **minikube** ≥ 1.30 (probado con driver `docker`).
- **kubectl** compatible con la versión del cluster.
- **GNU make**.
- **docker** (CLI) para construir la imagen custom del stack 8.
- Acceso a `docker.io` y `quay.io` (para tirar `mysql:5.7`, `mysql:8.0`, `mendhak/http-https-echo`, `python:3.12-slim`, `debezium/server:2.4.2.Final` y `quay.io/debezium/server:3.5.0.Final`).
- Recursos sugeridos en minikube:
  ```bash
  minikube start --cpus=4 --memory=6g
  ```
- Addons: el `storage-provisioner` (default en minikube) debe estar habilitado para los PVCs.

## Diferencias con docker-compose

| Aspecto | docker-compose | mini-kubernetes |
| --- | --- | --- |
| Aislamiento | red `cdc` por stack | namespace por stack (`cdc-mysql57`, `cdc-mysql8`) |
| Acceso host a MySQL | puertos host 3306-3309 | NodePort 30306-30309 |
| Config (`my.cnf`, init SQL, `application.properties`) | bind mounts | ConfigMaps |
| Password de root | env literal | Secret `mysql-credentials` |
| Carga: load-generator | venv en host (`make run-5.7` / `run-8`) | Job en-cluster on-demand (`make load-5.7` / `load-8`) |
| Imagen custom Debezium 3.5 | `docker build` ad hoc | `make image-build && make image-load` (minikube) |

## Levantar

Primera vez (ambos stacks):

```bash
cd mini-kubernetes
make image-build      # construye withreplica/debezium-server-mysql:3.5.0.Final
make image-load       # la carga al daemon de minikube
make up               # aplica los manifiestos de ambos stacks
make wait-healthy     # bloquea hasta que los 4 Pods MySQL estén Ready (puede tomar ~2 min)
```

Solo stack 5.7:

```bash
make up-5.7 && make wait-healthy-5.7
```

Solo stack 8 (incluye `image-load`):

```bash
make up-8 && make wait-healthy-8
```

## Verificar replicación

Stack 5.7 (sintaxis legacy):

```bash
kubectl exec -n cdc-mysql57 mysql-replica-0 -- \
  mysql -uroot -proot -e 'SHOW SLAVE STATUS\G' | grep -E 'Slave_(IO|SQL)_Running|Last_Error'
```

Esperado: `Slave_IO_Running: Yes` y `Slave_SQL_Running: Yes`.

```bash
kubectl exec -n cdc-mysql57 mysql-replica-0 -- \
  mysql -uroot -proot -e "SHOW VARIABLES LIKE 'log_slave_updates'"
```

Esperado: `ON`.

Stack 8 (sintaxis moderna):

```bash
kubectl exec -n cdc-mysql8 mysql-replica-0 -- \
  mysql -uroot -proot -e 'SHOW REPLICA STATUS\G' | grep -E 'Replica_(IO|SQL)_Running|Last_Error'
```

Esperado: `Replica_IO_Running: Yes` y `Replica_SQL_Running: Yes`.

```bash
kubectl exec -n cdc-mysql8 mysql-replica-0 -- \
  mysql -uroot -proot -e "SHOW VARIABLES LIKE 'log_replica_updates'"
```

Esperado: `ON`.

## Observar eventos CDC

```bash
make logs-sink-5.7    # eventos del stack 5.7
make logs-sink-8      # eventos del stack 8
```

Cada cambio en `inventory.customers` produce un POST con un body JSON parecido a:

```json
{
  "method": "POST",
  "path": "/",
  "body": "{\"schema\":...,\"payload\":{\"before\":null,\"after\":{\"id\":4,\"first_name\":\"Linus\",...},\"op\":\"c\",...}}"
}
```

Eventos en `inventory.audit_log` NO aparecen (control negativo del filtrado).

## Generar carga

```bash
make load-5.7         # lanza un Job en cdc-mysql57 (40s, ~40 ops)
make load-8           # lanza un Job en cdc-mysql8 (40s, ~40 ops)
```

Cada invocación crea un Job nuevo (gracias a `metadata.generateName`), por lo que puedes ejecutarlos varias veces sin colisión. Los Jobs se auto-borran 5 min después de terminar (`ttlSecondsAfterFinished: 300`).

Para seguir el progreso del Job más reciente:

```bash
kubectl get jobs -n cdc-mysql8
kubectl logs -n cdc-mysql8 -l app=load-generator --tail=-1 -f
```

## Acceso desde el host

Todas las instancias MySQL del lab están expuestas vía **NodePort** sobre la IP de minikube. Esa IP la obtienes con:

```bash
minikube ip          # típicamente algo como 192.168.49.2 o 192.168.58.2
```

### Mapa de conexiones

| Qué | Host | Puerto | User / Pass | DB inicial |
| --- | --- | --- | --- | --- |
| MySQL 5.7 — primary | `$(minikube ip)` | **30406** | `root` / `root` | `inventory` |
| MySQL 5.7 — **replica** | `$(minikube ip)` | **30407** | `root` / `root` | `inventory` |
| MySQL 8.0 — primary | `$(minikube ip)` | **30408** | `root` / `root` | `inventory` |
| MySQL 8.0 — **replica** | `$(minikube ip)` | **30409** | `root` / `root` | `inventory` |
| **Debezium state DB** (stack 5.7) | `$(minikube ip)` | **30410** | `dbz_state_57` / *(ver Secret)* | `dbz_state_57` |
| **Debezium state DB** (stack 8) | `$(minikube ip)` | **30410** | `dbz_state_8` / *(ver Secret)* | `dbz_state_8` |
| Debezium state DB (root) | `$(minikube ip)` | **30410** | `root` / *(ver Secret)* | — |

Los passwords del state DB están en el Secret `debezium-state-credentials`:

```bash
kubectl -n cdc-lab get secret debezium-state-credentials \
  -o jsonpath='{.data.dbz-state-8-password}' | base64 -d ; echo
kubectl -n cdc-lab get secret debezium-state-credentials \
  -o jsonpath='{.data.dbz-state-57-password}' | base64 -d ; echo
kubectl -n cdc-lab get secret debezium-state-credentials \
  -o jsonpath='{.data.root-password}' | base64 -d ; echo
```

### CLI

```bash
# Réplica stack 8
mysql -h $(minikube ip) -P 30409 -uroot -proot inventory

# Réplica stack 5.7
mysql -h $(minikube ip) -P 30407 -uroot -proot inventory

# State DB de Debezium (stack 8)
STATE_PWD=$(kubectl -n cdc-lab get secret debezium-state-credentials \
  -o jsonpath='{.data.dbz-state-8-password}' | base64 -d)
mysql -h $(minikube ip) -P 30410 -u dbz_state_8 -p"$STATE_PWD" dbz_state_8
```

En el state DB encontrarás las tablas `offset_storage` y `schema_history` que Debezium usa como cursor + caché de schemas.

### DBeaver

1. **Database → New Database Connection → MySQL**.
2. Server Host = output de `minikube ip` (ej. `192.168.58.2`). Port según la tabla de arriba. User/Password según la tabla.
3. En la pestaña **Driver properties** añade (necesario para MySQL 8 y para el state DB que también es MySQL 8):
   - `allowPublicKeyRetrieval` = `true`
   - `useSSL` = `false`
4. **Test Connection** → **Finish**.

### Acceso específico a la base de datos de Debezium state

El `mysql-debezium-state` es un MySQL compartido por ambos stacks que guarda dos cosas críticas para Debezium:

- **`offset_storage`** — última posición leída del binlog (cursor). Si se borra → re-snapshot completo.
- **`schema_history`** — DDL histórico de las tablas capturadas. Si se borra → Debezium no puede interpretar eventos viejos (requiere `snapshot.mode=when_needed` o re-snapshot).

Hay una DB por stack, aisladas: `dbz_state_57` y `dbz_state_8`. Cada una tiene su propio usuario sin grants cruzados.

**1) Obtener el password del usuario del stack que te interesa**

```bash
# Stack 8
kubectl -n cdc-lab get secret debezium-state-credentials \
  -o jsonpath='{.data.dbz-state-8-password}' | base64 -d ; echo

# Stack 5.7
kubectl -n cdc-lab get secret debezium-state-credentials \
  -o jsonpath='{.data.dbz-state-57-password}' | base64 -d ; echo

# Root (si necesitas ver ambas DBs o ejecutar TRUNCATE/DROP)
kubectl -n cdc-lab get secret debezium-state-credentials \
  -o jsonpath='{.data.root-password}' | base64 -d ; echo
```

**2) Conectarse con `mysql` CLI**

```bash
# Como dbz_state_8 (solo ve dbz_state_8, sin DROP/TRUNCATE)
STATE_PWD=$(kubectl -n cdc-lab get secret debezium-state-credentials \
  -o jsonpath='{.data.dbz-state-8-password}' | base64 -d)
mysql -h $(minikube ip) -P 30410 -u dbz_state_8 -p"$STATE_PWD" dbz_state_8

# Como root (ve ambas DBs, puede truncar)
ROOT_PWD=$(kubectl -n cdc-lab get secret debezium-state-credentials \
  -o jsonpath='{.data.root-password}' | base64 -d)
mysql -h $(minikube ip) -P 30410 -uroot -p"$ROOT_PWD"
```

**3) Conectarse con DBeaver**

| Campo | Valor |
| --- | --- |
| Driver | MySQL |
| Server Host | output de `minikube ip` (ej. `192.168.58.2`) |
| Port | `30410` |
| Database | `dbz_state_8` o `dbz_state_57` (vacío si entras como `root`) |
| Username | `dbz_state_8`, `dbz_state_57` o `root` |
| Password | el que obtuviste en el paso 1 |
| Driver properties → `allowPublicKeyRetrieval` | `true` |
| Driver properties → `useSSL` | `false` |

> El driver MySQL 8 de DBeaver rechaza el handshake sin `allowPublicKeyRetrieval=true` y se queja del certificado sin `useSSL=false`. Estos dos parámetros son obligatorios.

**4) Qué inspeccionar**

```sql
USE dbz_state_8;

-- Cursor actual: posición y GTID hasta donde leyó Debezium
SELECT * FROM offset_storage;

-- DDL histórico de las tablas capturadas
SELECT id, history_data_seq, record_insert_ts, LEFT(history_data, 200) AS preview
FROM schema_history
ORDER BY history_data_seq;
```

**5) Forzar re-snapshot (si Debezium quedó en `CrashLoopBackOff` porque los binlogs se purgaron)**

Necesita usuario `root` porque `dbz_state_*` no tiene `DROP` (que `TRUNCATE` requiere):

```bash
ROOT_PWD=$(kubectl -n cdc-lab get secret debezium-state-credentials \
  -o jsonpath='{.data.root-password}' | base64 -d)
mysql -h $(minikube ip) -P 30410 -uroot -p"$ROOT_PWD" -e "
  DELETE FROM dbz_state_8.offset_storage;
  DELETE FROM dbz_state_8.schema_history;"

kubectl -n cdc-lab rollout restart deploy/debezium-server-8
```

Asegúrate de que el ConfigMap tiene `debezium.source.snapshot.mode=when_needed` (no `initial`), si no Debezium volverá a fallar la siguiente vez que el binlog se purgue.

### Alternativas (sin depender de la IP de minikube)

Si la IP de minikube cambia con frecuencia o el driver no la expone directamente:

```bash
# Abre un túnel y te imprime la URL final
minikube service mysql-replica-nodeport-8 -n cdc-lab --url

# O port-forward al ClusterIP (siempre apunta a localhost)
kubectl -n cdc-lab port-forward svc/mysql-replica-8        13309:3306   # réplica 8
kubectl -n cdc-lab port-forward svc/mysql-debezium-state   13310:3306   # state DB
```

Y luego conectas con `mysql -h 127.0.0.1 -P 13309 ...`

## Limpieza

### Dentro del cluster (solo el laboratorio)

```bash
make down             # borra ambos namespaces (incluye PVCs)
make down-5.7         # solo stack 5.7
make down-8           # solo stack 8
```

`make down` es idempotente: no falla si los namespaces ya no existen. **El cluster minikube sigue corriendo**.

### El cluster entero (apagar / destruir)

| Comando | Qué hace | Cuándo |
| --- | --- | --- |
| `minikube stop` | Apaga el nodo, conserva PVCs, imágenes cargadas y configuración. `minikube start` lo levanta exacto como estaba. | Liberar RAM/CPU al final del día sin perder el lab. |
| `minikube delete` | Destruye el nodo. Se pierden imágenes locales (incluida la custom de Debezium), PVCs, y todo. | Empezar de cero o desinstalar. |

Flujo típico para volver a crearlo desde cero:

```bash
make down                                  # opcional; minikube delete también lo limpia
minikube delete                            # destruye el cluster

minikube start --cpus=4 --memory=6g        # crea uno nuevo
make image-build && make image-load        # vuelve a cargar la imagen custom
make up && make wait-healthy               # relevantar el laboratorio
```

Verificación rápida del estado del cluster:

```bash
minikube status                            # "Running" / "Stopped" / "Profile not found"
minikube profile list                      # cuántos clusters tienes y cuál es el activo
```

Ver `TUTORIAL.md` §11 para los detalles de cada comando.

## Estructura de archivos

```
mini-kubernetes/
├── Makefile
├── README.md
├── mysql5.7/
│   ├── 00-namespace.yaml
│   ├── 01-configmaps.yaml          # 6 ConfigMaps: configs MySQL + init SQL + healthcheck + Debezium
│   ├── 02-secrets.yaml             # mysql-credentials
│   ├── 03-mysql-primary.yaml       # StatefulSet + Service headless + Service NodePort
│   ├── 04-mysql-replica.yaml       # StatefulSet (con initContainer wait-for-primary) + Services
│   ├── 05-cdc-sink.yaml            # Deployment + Service ClusterIP
│   └── 06-debezium-server.yaml     # Deployment + PVC debezium-data
├── mysql8/
│   └── (estructura idéntica con sintaxis moderna y imagen custom 3.5)
└── load-generator/
    ├── mysql5.7/                        # kustomize root para cdc-mysql57
    │   ├── kustomization.yaml           # configMapGenerator: load-generator-script
    │   ├── random_changes.py            # copia del script (montada como ConfigMap)
    │   └── requirements.txt
    ├── mysql8/                          # kustomize root para cdc-mysql8 (estructura idéntica)
    │   ├── kustomization.yaml
    │   ├── random_changes.py
    │   └── requirements.txt
    ├── job-mysql5.7.yaml                # Job en cdc-mysql57 (40s)
    └── job-mysql8.yaml                  # Job en cdc-mysql8 (40s)
```

> El ConfigMap `load-generator-script` se genera con kustomize (`kubectl apply -k load-generator/mysql8/`) en lugar de definirlo en un YAML inline. Esto evita duplicar ~200 líneas del script Python en YAML. Ver `TUTORIAL.md` §6 para los detalles.

## Troubleshooting

### La réplica no arranca / `Slave_IO_Running` o `Replica_IO_Running` reporta `No`

```bash
kubectl logs -n cdc-mysql57 mysql-replica-0           # stack 5.7
kubectl logs -n cdc-mysql8  mysql-replica-0           # stack 8
```

Causas típicas:

- El initContainer `wait-for-primary` aún no terminó porque el primary no había replicado el usuario `repl`. Espera un poco más o reinicia con `kubectl delete pod -n <ns> mysql-replica-0` para forzar un reintento.
- `01-start-replica.sql` no se ejecutó porque la réplica ya tenía datadir. Para forzar un re-init borra el PVC: `kubectl delete pvc -n <ns> data-mysql-replica-0 && kubectl delete pod -n <ns> mysql-replica-0`.

### Debezium no se conecta a la réplica

```bash
kubectl logs -n cdc-mysql8 deploy/debezium-server
```

- Verifica que el usuario `debezium` llegó replicado a la réplica:
  ```bash
  kubectl exec -n cdc-mysql8 mysql-replica-0 -- \
    mysql -uroot -proot -e "SELECT user, plugin FROM mysql.user WHERE user='debezium'"
  ```
- Verifica que el ConfigMap `debezium-config` apunta a `mysql-replica` (no a `mysql-primary`):
  ```bash
  kubectl get cm -n cdc-mysql8 debezium-config -o jsonpath='{.data.application\.properties}' | grep hostname
  ```

### No veo eventos en `cdc-sink` aunque inserto en el primary

Causa #1: la réplica no tiene `log_slave_updates`/`log_replica_updates` activo, por lo que los cambios replicados no se re-loguean en su binlog y Debezium nunca los ve.

```bash
kubectl exec -n cdc-mysql57 mysql-replica-0 -- \
  mysql -uroot -proot -e "SHOW VARIABLES LIKE 'log_slave_updates'"
kubectl exec -n cdc-mysql8 mysql-replica-0 -- \
  mysql -uroot -proot -e "SHOW VARIABLES LIKE 'log_replica_updates'"
```

Debe devolver `ON`. Si está en `OFF`, revisa el ConfigMap `mysql-replica-config` y reinicia el pod (con borrado de PVC para re-init).

Causa #2: estás insertando en `audit_log` (excluido del filtro). Inserta en `inventory.customers`.

### `Image withreplica/debezium-server-mysql:3.5.0.Final not found`

La imagen no llegó al daemon de minikube. Repite:

```bash
make image-build
make image-load
minikube image ls | grep withreplica   # debe listarla
kubectl rollout restart deploy/debezium-server -n cdc-mysql8
```

### `make up` falla con `error: unable to recognize ... namespaces "cdc-mysqlX" not found`

Esto puede pasar si `kubectl apply -f mysql8/` aplica recursos en orden alfabético y un recurso intenta crearse antes que el namespace. El orden de los archivos (`00-namespace.yaml`, `01-...`) está pensado para que esto no ocurra, pero si pasa, ejecuta dos veces — la segunda funcionará.

### Quiero forzar un re-snapshot de Debezium

```bash
kubectl delete pvc -n cdc-mysql8 debezium-data
kubectl rollout restart deploy/debezium-server -n cdc-mysql8
```

(Equivalente a borrar el volumen `debezium-data` del docker-compose.)

### Cómo cambiar puertos / tablas observadas

| Qué | Dónde |
| --- | --- |
| NodePort del primary/replica | `mysql<5.7\|8>/03-mysql-primary.yaml` y `04-mysql-replica.yaml`, campo `nodePort:` |
| Password de root | Secret `mysql-credentials` (`02-secrets.yaml`) — pero recuerda que las contraseñas de `repl` y `debezium` están en `01-configmaps.yaml` y en `application.properties` |
| Tablas observadas por Debezium | ConfigMap `debezium-config` en `01-configmaps.yaml`, propiedad `debezium.source.table.include.list` |

Después de modificar el ConfigMap de Debezium:

```bash
kubectl apply -f mysql8/01-configmaps.yaml
kubectl delete pvc -n cdc-mysql8 debezium-data   # si cambiaste el set de tablas
kubectl rollout restart deploy/debezium-server -n cdc-mysql8
```

### Comandos útiles para Kubernetes

#### Todos los pods
kubectl get pods --all-namespaces

#### Todos los pods de un namespace
kubectl get pods -n cdc-mysql8

#### Filtrar por label (lo que hemos usado en el experimento)
kubectl get pods -n cdc-mysql8 -l app=debezium-server

#### En todos los namespaces
kubectl get pods --all-namespaces            # alias: -A

#### Con más info (IP, nodo, edad)
kubectl get pods -n cdc-mysql8 -o wide

#### Watch (refresca al cambiar)
kubectl get pods -n cdc-mysql8 -w

#### Detener un pod

Importante: en Kubernetes "detener" un pod = borrarlo. Si está manejado por un Deployment (como debezium-server), k8s lo recrea automáticamente. Para detenerlo de verdad hay que
  bajar el Deployment.

#### Borrar un pod específico (el Deployment lo recreará)
kubectl delete pod <nombre-pod> -n cdc-mysql8

#### Borrar por label (lo que usa el experimento)
kubectl delete pod -l app=debezium-server -n cdc-mysql8

#### Borrar forzado e inmediato (sin grace period) — lo que usamos para medir RTO
kubectl delete pod -l app=debezium-server -n cdc-mysql8 --grace-period=0 --force

#### Detener "de verdad" un servicio gestionado por Deployment:
#### escalar a 0 réplicas (no se recrea hasta que vuelvas a escalar)
kubectl scale deployment debezium-server -n cdc-mysql8 --replicas=0

#### Volver a levantarlo
kubectl scale deployment debezium-server -n cdc-mysql8 --replicas=1