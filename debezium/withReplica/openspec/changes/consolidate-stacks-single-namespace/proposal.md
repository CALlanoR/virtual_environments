## Why

Tras `migrate-debezium-state-to-mysql`, el lab tiene dos namespaces (`cdc-mysql57` y `cdc-mysql8`) cada uno con su propia copia de la infraestructura, incluido un `mysql-debezium-state` per stack. Esa decisión (Decisión 1 del change anterior) hizo cada stack autocontenido, pero introduce dos costos que ahora dejaron de tener justificación:

1. **Duplicación de infraestructura mínima.** Dos PVCs de 500Mi, dos Pods de MySQL para state, dos Services, dos Secrets. En el lab de un solo nodo eso es ruido sin beneficio.
2. **Divergencia con el modelo de producción.** En producción la base de datos vive fuera de Kubernetes y se asume una sola para el state de CDC (no una por origen). Per-stack en el lab no refleja esa realidad.

Adicionalmente, mantener dos namespaces obliga a contextualizar cada comando `kubectl` (`-n cdc-mysql57` vs `-n cdc-mysql8`) y a duplicar pasos en scripts/Makefile. Para un lab donde el operador trabaja con ambos stacks en paralelo, un namespace único reduce fricción operativa sin perder aislamiento lógico (eso lo da los labels y los nombres con sufijo).

## What Changes

### Consolidación a un solo namespace

- **Nuevo namespace único `cdc-lab`** que contiene los dos stacks completos.
- Los namespaces `cdc-mysql57` y `cdc-mysql8` se eliminan al final del change (después de validar que `cdc-lab` funciona).

### Renombrado de recursos con sufijo `-57` / `-8`

Cada recurso que existía duplicado en ambos namespaces se renombra con sufijo del stack. La nomenclatura aplica a Services, Deployments, StatefulSets, ConfigMaps, Secrets, Jobs y Pods. Etiqueta `stack=mysql57` o `stack=mysql8` agregada a todos para facilitar selectores.

| Antes (cada uno en su namespace) | Después (todos en `cdc-lab`) |
|---|---|
| `mysql-primary` | `mysql-primary-57`, `mysql-primary-8` |
| `mysql-replica` | `mysql-replica-57`, `mysql-replica-8` |
| `cdc-sink` | `cdc-sink-57`, `cdc-sink-8` |
| `debezium-server` | `debezium-server-57`, `debezium-server-8` |
| ConfigMap `debezium-config` | `debezium-config-57`, `debezium-config-8` |
| ConfigMap `mysql-primary-config` | `mysql-primary-config-57`, `mysql-primary-config-8` |
| (idem el resto de ConfigMaps por-stack) | sufijo `-57` / `-8` |
| Secret `mysql-credentials` | `mysql-credentials-57`, `mysql-credentials-8` |

### State-store único compartido

- Un solo `mysql-debezium-state` (Deployment + Service + PVC) en el namespace `cdc-lab`. **No** lleva sufijo porque es único.
- Dos bases de datos lógicas dentro del mismo MySQL: `dbz_state_57` y `dbz_state_8`.
- Dos usuarios separados (`dbz_state_57`, `dbz_state_8`) con grants `SELECT, INSERT, UPDATE, DELETE, CREATE` **solo sobre su propia DB**. Aislamiento lógico: un Debezium no puede leer ni dañar el state del otro.
- Un solo Secret `debezium-state-credentials` con cuatro keys: `root-password`, `dbz-state-57-password`, `dbz-state-8-password`.
- JDBC URLs por stack:
  - mysql5.7 → `jdbc:mysql://mysql-debezium-state:3306/dbz_state_57?useSSL=false`
  - mysql8 → `jdbc:mysql://mysql-debezium-state:3306/dbz_state_8?useSSL=false`

### Reorganización de manifests

- Mantener directorios `minikube/mysql5.7/` y `minikube/mysql8/` (organizan los manifests por stack para legibilidad), pero cada manifest declara `namespace: cdc-lab` en lugar del namespace per-stack.
- Mover `mysql-debezium-state` a una nueva ubicación neutral: `minikube/shared/04a-mysql-debezium-state.yaml`.
- Crear `minikube/shared/00-namespace.yaml` con la declaración del namespace `cdc-lab`.

### Actualizaciones colaterales

- **`minikube/Makefile`**: targets `up`/`down`/`ps`/`logs-sink-*`/`load-*` reescritos para usar `cdc-lab` y selectores por label. `wait-healthy-5.7` y `wait-healthy-8` siguen existiendo, pero seleccionan por `-l stack=mysql57` / `stack=mysql8` en lugar de cambiar de namespace.
- **`minikube/scripts/rto_measure.py`**: ahora acepta un selector de label (no solo namespace). Llamada típica: `python3 rto_measure.py cdc-lab 3 mysql8-auto --label-selector app=debezium-server-8`.
- **`minikube/scripts/rto_experiment.sh`**: ajustado a la nueva estructura. Tabla resumen reporta por `stack=mysql57` y `stack=mysql8`.
- **`minikube/scripts/loadgen-long.yaml`**: el placeholder `__NAMESPACE__` se reemplaza siempre por `cdc-lab`; se agrega un nuevo placeholder `__STACK_LABEL__` para el sufijo (`-57` / `-8`) en el nombre del Job y la etiqueta `stack`.

### Migración

- Greenfield: se aplica el namespace nuevo desde cero. No se migra el offset del state-store viejo. Debezium hará re-snapshot inicial al levantar (trivial en el lab).
- Borrar los namespaces `cdc-mysql57` y `cdc-mysql8` al final, después de confirmar que `cdc-lab` está sano.

## Capabilities

### Modified Capabilities
- `debezium-server-ha`: se refinan los requirements de "MySQL state-store dedicado" para reflejar la consolidación a un único state-store con dos DBs y dos usuarios; se refina el requirement de la "Configuración actual" para apuntar al namespace `cdc-lab` en lugar de `cdc-mysql57`/`cdc-mysql8`.

## Impact

- **Manifests Kubernetes:** todos los archivos de `minikube/mysql5.7/` y `minikube/mysql8/` se modifican (namespace + renombres). Se crean `minikube/shared/00-namespace.yaml` y `minikube/shared/04a-mysql-debezium-state.yaml`. Los archivos `04a-mysql-debezium-state.yaml` por-stack se eliminan.
- **Documentación / specs:** se modifica la capability `debezium-server-ha` (3 requirements actualizados; 1 nuevo para el aislamiento por DB lógica).
- **Scripts:** `rto_measure.py` y `rto_experiment.sh` se actualizan para soportar discriminación por label. `loadgen-long.yaml` agrega un placeholder.
- **Makefile:** todos los targets que referencian namespace cambian a `cdc-lab` con selectores por label.
- **Operación:** durante la migración hay una ventana donde ambos stacks están abajo (mientras se borran los namespaces viejos y arranca el nuevo). En el lab esto es aceptable (~1-2 minutos). En producción el patrón equivalente sería un blue-green con un cluster nuevo y cutover; fuera del alcance.
- **Dependencias externas:** ninguna.

## Aplicabilidad a producción

Este cambio **acerca el lab al modelo productivo** real:
- En producción la DB (primary + replica) vive **fuera de Kubernetes**. El cluster solo corre Debezium servers y el sink. Un único namespace para todo lo de CDC es más representativo de lo que se va a deployar allá.
- En producción habrá **un único state-store** (managed o dedicado), no uno por origen. Consolidar a uno en el lab valida el patrón.

Lo que sigue siendo `lab-only`: que `mysql-primary-*` y `mysql-replica-*` vivan en el cluster (en prod son externos), y el namespace `cdc-lab` (en prod probablemente sea simplemente `cdc` o el namespace del equipo).
