# mini-kubernetes — Debezium Server con offset en archivo (PVC)

Variante del laboratorio en la que Debezium **persiste su estado (offset + schema history) en archivos locales** del pod, respaldados por un `PersistentVolumeClaim`. Es el contrapunto experimental de la variante hermana [`../debeziumWithOffSetInDatabase/`](../debeziumWithOffSetInDatabase/), que almacena lo mismo en un MySQL dedicado.

Reproduce los dos stacks (`mysql5.7` + `mysql8`) en el namespace único `cdc-lab-file`, distinguidos por la label `stack`.

| Stack | Namespace | MySQL | Debezium Server | NodePort primary / replica |
| --- | --- | --- | --- | --- |
| 5.7 | `cdc-lab-file` | 5.7 | `withreplica/debezium-server-mysql57-jdbc:2.4.2.Final` (build local) | **30506** / **30507** |
| 8.0 | `cdc-lab-file` | 8.0 | `withreplica/debezium-server-mysql:3.5.0.Final` (build local sobre quay.io) | **30508** / **30509** |

A diferencia de la variante con DB, **aquí no existe ni `mysql-debezium-state` ni NodePort 30410** — el estado es 100% archivo dentro del pod.

> **El monitoreo no está incluido.** Lo que existe en `../../docker-compose/monitoring/` queda fuera del alcance.

## Diferencias frente a `debeziumWithOffSetInDatabase`

| Aspecto | …WithOffSetInDatabase | …WithOffSetInFile (esta variante) |
| --- | --- | --- |
| Donde vive el offset | Tabla `offset_storage` en MySQL `mysql-debezium-state` | Archivo `/debezium/data/offsets-<stack>.dat` |
| Donde vive el schema history | Tabla `schema_history` en el mismo MySQL | Archivo `/debezium/data/schema-history-<stack>.dat` |
| Backing-store class | `io.debezium.storage.jdbc.offset.JdbcOffsetBackingStore` + `io.debezium.storage.jdbc.history.JdbcSchemaHistory` | `org.apache.kafka.connect.storage.FileOffsetBackingStore` + `io.debezium.storage.file.history.FileSchemaHistory` |
| Persistencia del estado | DB con su propio PVC (`debezium-state-data`) | PVC dedicado por stack (`debezium-data-57`, `debezium-data-8`) |
| Recursos extra desplegados | Deployment + Service + Secret + ConfigMap del MySQL state | Ninguno (solo el PVC) |
| Recuperación si el archivo / tabla se pierde | `DELETE FROM offset_storage; DELETE FROM schema_history;` + restart | `kubectl delete pvc debezium-data-<stack>` + restart |
| Cómo inspeccionar el cursor | `SELECT * FROM offset_storage` desde un cliente SQL | `kubectl exec ... cat /debezium/data/offsets-<stack>.dat` |
| Aptitud para HA | Soporta múltiples instancias contra la misma DB | Solo un pod a la vez (PVC ReadWriteOnce) |

## Topología

```
┌─────────────────────────────  namespace cdc-lab-file  (stack mysql8)  ─────────────────────────────┐
│                                                                                               │
│  ┌──────────────────┐  replicación   ┌──────────────────┐  binlog    ┌────────────────────┐   │
│  │ mysql-primary-8  │ ─────────────▶ │ mysql-replica-8  │ ─────────▶ │ debezium-server-8  │   │
│  │ (StatefulSet)    │   (GTID, ROW)  │ (StatefulSet)    │            │ (Deployment, 1pod) │   │
│  └──────────────────┘                └──────────────────┘            └─────┬──────────────┘   │
│        ▲ NodePort 30508                  NodePort 30509                    │ HTTP             │
│        │                                                                   │ POST             │
│   tu cliente / Job                                                         ▼                  │
│                                                                    ┌────────────────┐         │
│                                                                    │   cdc-sink-8   │         │
│                                                                    │ (Deployment)   │         │
│                                                                    └────────────────┘         │
│                                                                                               │
│   PVC debezium-data-8  (RWO, 1Gi)  →  /debezium/data/{offsets-8.dat, schema-history-8.dat}    │
└───────────────────────────────────────────────────────────────────────────────────────────────┘
```

El stack 5.7 es estructuralmente idéntico, con NodePorts 30506/30507 y PVC `debezium-data-57`.

## Prerrequisitos

- **minikube** ≥ 1.30 (probado con driver `docker`).
- **kubectl** compatible con la versión del cluster.
- **GNU make**.
- **docker** (CLI) para construir las dos imágenes custom de Debezium.
- Recursos sugeridos:
  ```bash
  minikube start --cpus=4 --memory=6g
  ```

## Levantar

```bash
cd debeziumWithOffSetInFile
make image-build      # imagen Debezium 3.5 (stack 8)
make image-load
make image-build-57   # imagen Debezium 2.4 + JDBC (stack 5.7) — no usamos JDBC para el offset
make image-load-57    # pero la imagen sigue siendo la misma para mantener paridad
make up               # aplica namespace + ambos stacks + load-generators
make wait-healthy     # bloquea hasta que los 4 Pods MySQL estén Ready
```

> La imagen del stack 5.7 incluye el driver JDBC aunque aquí no lo usemos para el estado — así la imagen es la misma que en la variante hermana y puedes saltar entre ambas sin reconstruir.

## Observar eventos CDC

```bash
make logs-sink-5.7    # eventos del stack 5.7
make logs-sink-8      # eventos del stack 8
```

## Generar carga

```bash
make load-5.7
make load-8
```

## Acceso al archivo de offset

Aquí está la parte central de esta variante. El archivo `offsets-<stack>.dat` es un **serializado Java** (no texto plano), por eso necesitas leerlo con herramientas que lo decodifiquen.

### 1) Localizar el pod

```bash
kubectl -n cdc-lab-file get pods -l app=debezium-server,stack=mysql8 -o name
# pod/debezium-server-8-xxxxxxxx-yyyyy
```

### 2) Listar los archivos dentro del pod

```bash
POD=$(kubectl -n cdc-lab-file get pods -l app=debezium-server,stack=mysql8 -o jsonpath='{.items[0].metadata.name}')
kubectl -n cdc-lab-file exec $POD -- ls -la /debezium/data
```

Esperado:

```
-rw-r--r-- 1 jboss jboss   190 May 19 10:01 offsets-8.dat
-rw-r--r-- 1 jboss jboss  4567 May 19 10:01 schema-history-8.dat
```

### 3) Ver el contenido del offset (legible)

El formato es `ObjectOutputStream` de Java sobre un `Map<ByteBuffer, ByteBuffer>`. La imagen de Debezium es UBI minimal — no incluye `strings` (que vive en `binutils`). Usa `tr` para descartar los bytes no imprimibles y `grep` para filtrar ruido corto:

```bash
kubectl -n cdc-lab-file exec $POD -- sh -c \
  "cat /debezium/data/offsets-8.dat | tr -c '[:print:]\n' '\n' | grep -vE '^.{0,3}\$'"
```

Salida típica:

```
java.util.HashMap
loadFactorI
thresholdxp?@
#["http",{"server":"replica-cdc-8"}]uq
{"ts_sec":1779218623,"file":"mysql-bin.000003","pos":3001012,"gtids":"06598408-...:1-15,1567900d-...:1-5"}x
```

Lo importante: el JSON con `file`, `pos` y `gtids` — eso es el cursor que Debezium retomará tras un restart. El resto del output (cabecera `java.util.HashMap`, `loadFactor`, etc.) es metadata de la serialización Java y se ignora.

**Alternativa — extraer al host y usar `strings` local:**

```bash
kubectl -n cdc-lab-file cp $POD:/debezium/data/offsets-8.dat ./offsets-8.dat
strings ./offsets-8.dat                   # si tienes binutils en tu host (típico Linux)
```

### 4) Ver el schema history

```bash
kubectl -n cdc-lab-file exec $POD -- cat /debezium/data/schema-history-8.dat | head -20
```

A diferencia del offset, este sí es **texto** (JSON Lines): una línea por DDL capturada.

```json
{"source":{"server":"replica-cdc-8"},"position":{"ts_sec":...},"databaseName":"inventory",
 "ddl":"CREATE TABLE `customers` (`id` int NOT NULL AUTO_INCREMENT, ...)","tableChanges":[...]}
```

### 5) Copiar el archivo a tu host (opcional)

Si prefieres analizar offline o respaldarlo:

```bash
kubectl -n cdc-lab-file cp $POD:/debezium/data/offsets-8.dat        ./offsets-8.dat
kubectl -n cdc-lab-file cp $POD:/debezium/data/schema-history-8.dat ./schema-history-8.dat
```

## Preguntas conceptuales

### ¿Qué pasa si en un ambiente real el pod cambia de máquina (nodo) del cluster?

Depende de **qué clase de volumen (StorageClass)** respalda al PVC `debezium-data-<stack>`:

1. **StorageClass de red (lo correcto en producción)** — ejemplos: AWS EBS, GCP Persistent Disk, Azure Disk, Ceph RBD, Longhorn, NFS.

   El PVC es **un objeto del control plane** desacoplado del nodo. Cuando el scheduler decide mover el pod a otro nodo (por evicción, drain, fallo del nodo, etc.):

   - El volumen viejo se **detach** del nodo anterior y se **attach** al nuevo.
   - El pod arranca en el nuevo nodo y monta el mismo volumen → ve los archivos `offsets-*.dat` y `schema-history-*.dat` intactos.
   - Debezium retoma desde el último offset. **No hay re-snapshot.**

   El pod no "va donde está el archivo"; **el archivo viaja con el pod**, intermediado por el control plane. Es transparente para la aplicación.

2. **`hostPath` o `local-path` provisioner (es lo que da minikube por default)** — el volumen vive en el disco del nodo concreto.

   Aquí sí hay anclaje al nodo:

   - El PVC obtiene un `nodeAffinity` que **fija** al pod al nodo donde se creó el volumen.
   - Si ese nodo desaparece, el pod queda en `Pending` indefinidamente — no se puede mover porque el archivo es físicamente inalcanzable desde otro nodo.
   - Recuperación: borrar el PVC para forzar re-snapshot en otro nodo (pérdida del cursor).

   En minikube con un solo nodo esto es invisible. En producción **es un anti-patrón** para datos de estado.

### ¿El pod va siempre donde está el archivo, o el archivo se mueve con el pod?

Lo segundo, en un cluster bien configurado. El modelo k8s es:

- **El pod es efímero** (puede recrearse, moverse, escalarse).
- **El PVC es la unidad estable** (representa "necesito 1Gi de almacenamiento persistente").
- El **PersistentVolume** subyacente (el volumen real) lo provisiona la StorageClass y normalmente es independiente del nodo.

Cuando el pod se reprograma, k8s primero hace **detach** del PV en el nodo viejo y luego **attach** en el nuevo antes de arrancar el contenedor. Para el código de Debezium, el archivo "siempre estuvo en `/debezium/data/offsets-8.dat`" — no sabe ni le importa qué nodo es.

La excepción son volúmenes locales (`hostPath`, `local`): ahí sí el pod queda anclado al nodo. Por eso `hostPath` nunca debe usarse en producción para datos críticos como el offset de un CDC.

### ¿Qué garantiza que dos pods no escriban al mismo archivo simultáneamente?

Tres capas:

1. **`accessModes: ["ReadWriteOnce"]`** en el PVC: el storage subyacente solo permite que **un nodo a la vez** monte el volumen.
2. **`strategy: Recreate`** en el Deployment: durante un rollout, el pod viejo se termina **antes** de arrancar el nuevo. Con `RollingUpdate` los dos coexistirían un momento y el nuevo no podría montar el volumen (`MountVolume.SetUp failed: volume is already exclusively attached`).
3. **`replicas: 1`** — no hay escalamiento horizontal. Esta variante no soporta HA activo-activo; para HA habría que pasarse a la variante con DB y dos instancias con el mismo `topic.prefix`.

### ¿Y si quiero forzar un re-snapshot (equivalente a borrar las tablas en la variante DB)?

```bash
kubectl -n cdc-lab-file scale deployment/debezium-server-8 --replicas=0   # libera el PVC
kubectl -n cdc-lab-file delete pvc debezium-data-8                        # borra el archivo
kubectl -n cdc-lab-file apply -f mysql8/06-debezium-server-8.yaml         # recrea el PVC vacío
kubectl -n cdc-lab-file scale deployment/debezium-server-8 --replicas=1
```

Asegúrate de tener `debezium.source.snapshot.mode=when_needed` en el ConfigMap (ya está así). Con `initial` también funciona porque al no haber offset previo, Debezium hace snapshot automático.

## Acceso desde el host (MySQL)

Esta variante usa NodePorts distintos (rango **305xx** en vez de **304xx**) para no chocar con la variante con DB si la corres en paralelo. Tampoco expone un state DB, así que no hay NodePort equivalente al `30410` de la variante hermana.

```bash
mysql -h $(minikube ip) -P 30508 -uroot -proot inventory   # primary stack 8
mysql -h $(minikube ip) -P 30509 -uroot -proot inventory   # replica stack 8
mysql -h $(minikube ip) -P 30506 -uroot -proot inventory   # primary stack 5.7
mysql -h $(minikube ip) -P 30507 -uroot -proot inventory   # replica stack 5.7
```

## Limpieza

```bash
make down             # borra todo el namespace cdc-lab-file (incluye PVCs de Debezium)
make down-5.7         # solo recursos del stack 5.7
make down-8           # solo recursos del stack 8
```

> `down-5.7` y `down-8` borran también los PVCs `debezium-data-*` porque tienen la label `stack`. Si quieres preservar el archivo de offset al bajar el stack, primero quítale temporalmente la label:
>
> ```bash
> kubectl -n cdc-lab-file label pvc debezium-data-8 stack-
> ```

## Troubleshooting

### El pod queda en `Pending` con `1 node(s) didn't find available persistent volumes to bind`

Tu cluster no tiene un provisionador dinámico para la StorageClass por defecto. En minikube esto se arregla habilitando el addon:

```bash
minikube addons enable storage-provisioner
```

### El pod queda en `ContainerCreating` con `Multi-Attach error for volume`

Hay un pod viejo que aún no liberó el volumen (típico tras `kubectl delete pod --force` o cuando el nodo crashea). Espera 2-6 minutos a que k8s haga el detach forzado, o usa:

```bash
kubectl -n cdc-lab-file scale deployment/debezium-server-8 --replicas=0
# espera a que se libere
kubectl -n cdc-lab-file scale deployment/debezium-server-8 --replicas=1
```

### `Permission denied` al escribir `/debezium/data/offsets-8.dat`

El contenedor corre como UID 185 (`jboss`). Si tu StorageClass crea el PV con permisos del root del nodo, el pod no podrá escribir. En producción esto se arregla con `fsGroup: 185` en el `securityContext` del pod. En minikube con `storage-provisioner` no suele pasar porque crea los hostPath con permisos abiertos.

### Debezium reinicia sin parar tras restaurar un backup del archivo

Si copiaste un `offsets-*.dat` viejo y los binlogs ya se purgaron en la réplica, verás el mismo `CrashLoopBackOff` que en la variante DB. La solución es la misma: borrar el PVC para forzar re-snapshot, o asegurarte de que `snapshot.mode=when_needed`.
