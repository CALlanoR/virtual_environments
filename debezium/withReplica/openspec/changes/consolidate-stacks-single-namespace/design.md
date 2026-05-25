## Context

Tras `migrate-debezium-state-to-mysql`, el lab corre dos namespaces (`cdc-mysql57`, `cdc-mysql8`), cada uno con: `mysql-primary`, `mysql-replica`, `cdc-sink`, `debezium-server`, `mysql-debezium-state` (cada uno con su propio PVC, ConfigMap initdb, Secret y Service). El usuario aclaró que el modelo productivo es: DB fuera de Kubernetes, **un solo** state-store CDC. Mantener dos namespaces y dos state-stores en el lab introduce divergencia operativa y de arquitectura sin beneficio.

Este change consolida ambos stacks a un namespace único `cdc-lab` y un único `mysql-debezium-state` compartido (con dos bases de datos lógicas y dos usuarios separados para preservar el aislamiento entre stacks). El nombre del namespace es ajustable antes de aplicar; `cdc-lab` es la propuesta por descriptivo y porque sigue la convención `cdc-*` del lab.

## Goals / Non-Goals

**Goals:**
- Un único namespace `cdc-lab` con los dos stacks completos + el state-store compartido.
- Un único Pod de `mysql-debezium-state` que sirve a ambos Debezium server.
- Aislamiento lógico entre stacks: nombres con sufijo `-57` / `-8`, labels `stack=mysql57|mysql8`, dos DBs lógicas en el state-store, dos usuarios sin permisos cruzados.
- El Makefile, los scripts de RTO y el load-generator se actualizan para operar con la nueva estructura.

**Non-Goals:**
- Migrar el offset del state-store viejo al nuevo. Greenfield: re-snapshot inicial de `inventory.customers` (trivial en el lab).
- Cambiar la arquitectura HA del propio state-store (sigue siendo 1 réplica, 1 PVC). HA del state-store es otro change si se necesita.
- Reescribir `00-namespace.yaml` de cada stack para apuntar al mismo namespace. En su lugar, se elimina y se crea `minikube/shared/00-namespace.yaml`.
- Renombrar los directorios `minikube/mysql5.7/` y `minikube/mysql8/`. Se mantienen como organización lógica de los manifests.
- Cambiar la lógica de los Debezium (replicas, strategy, probes, resources). Eso fue alcance de changes previos.

## Decisions

### Decisión 1 — Namespace único `cdc-lab`

**Elegido:** crear un namespace nuevo `cdc-lab` y mover todo allí. Los namespaces `cdc-mysql57` y `cdc-mysql8` se borran al cierre del change.

**Razones:**
- Único namespace = un solo `-n` en cualquier comando.
- Sigue la convención `cdc-*` del lab (alineado con los archivos viejos).
- "lab" es descriptivo: este namespace no pretende ser productivo.

**Alternativa descartada:** reusar uno de los existentes (`cdc-mysql8` por ejemplo). Cargar la semántica histórica del nombre con todo el contenido sería confuso. Mejor un namespace nuevo limpio.

### Decisión 2 — Convención de nombres: sufijo `-57` / `-8`

**Elegido:** todos los recursos que existían por-stack se renombran con sufijo del stack. Excepción: `mysql-debezium-state` (único, sin sufijo). Ejemplos:

| Tipo de recurso | Antes | Después |
|---|---|---|
| StatefulSet | `mysql-primary` | `mysql-primary-57`, `mysql-primary-8` |
| Service | `mysql-replica` | `mysql-replica-57`, `mysql-replica-8` |
| Deployment | `debezium-server` | `debezium-server-57`, `debezium-server-8` |
| ConfigMap | `debezium-config` | `debezium-config-57`, `debezium-config-8` |
| Secret | `mysql-credentials` | `mysql-credentials-57`, `mysql-credentials-8` |

**Razones:**
- Sufijo lee mejor que prefijo en `kubectl get pods`: agrupa por tipo de recurso (todos los `mysql-primary-*` quedan juntos en listings alfabéticos).
- Más fácil de buscar con tab-complete: `mysql-primary-<tab>` lista solo los dos stacks.
- Convención numérica simple (`-57` y `-8`), no requiere recordar nombres compuestos.

**Alternativa descartada:** prefijo (`mysql57-primary`). Funcional pero menos legible en listings.

### Decisión 3 — Labels con `stack=mysql57` o `stack=mysql8`

Todo Pod, Service, Deployment, StatefulSet, ConfigMap y Secret asociado a un stack lleva `metadata.labels.stack: mysql57` o `mysql8`. Esto permite selectores rápidos: `kubectl get pods -l stack=mysql57` lista todo el stack 5.7.

El label `app=<componente>` se mantiene con su valor original (`mysql-primary`, `debezium-server`, etc.) **sin** sufijo, para que selectores como `app=debezium-server` retornen los dos Debezium del lab. Si quiero solo el de 5.7, combino: `-l app=debezium-server,stack=mysql57`.

### Decisión 4 — Un único `mysql-debezium-state` con dos DBs lógicas

**Elegido:** un Deployment `mysql-debezium-state` (sin sufijo) en `cdc-lab`. Dentro de ese MySQL hay dos bases de datos: `dbz_state_57` y `dbz_state_8`, cada una con sus tablas `offset_storage` y `schema_history`. Dos usuarios:

```sql
CREATE USER 'dbz_state_57'@'%' IDENTIFIED WITH mysql_native_password BY '<pw_57>';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE ON dbz_state_57.* TO 'dbz_state_57'@'%';

CREATE USER 'dbz_state_8'@'%'  IDENTIFIED WITH mysql_native_password BY '<pw_8>';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE ON dbz_state_8.*  TO 'dbz_state_8'@'%';
```

**Razones:**
- Aislamiento lógico: el usuario del stack 5.7 no puede leer ni escribir en `dbz_state_8`. Si Debezium del stack 5.7 se compromete o se mal-configura, no contamina el offset del stack 8.
- Operación: un solo Pod a monitorear, un solo PVC, un solo Service.
- Coincide con cómo se vería en producción (un cluster MySQL compartido de "metadata CDC" con DBs por consumidor).

**Alternativa descartada:** una sola DB con tablas separadas (`offset_storage_57`, `offset_storage_8`). Funciona pero el aislamiento de permisos sería más débil (el usuario tendría que tener grants a nivel de tabla, no de DB). Por DB es más simple.

**Alternativa descartada:** un solo usuario con grants a ambas DBs. Pierde aislamiento — un mal comportamiento del Debezium del 5.7 podría tocar tablas del 8. No vale el ahorro de un Secret.

### Decisión 5 — Un único Secret `debezium-state-credentials` con keys por stack

```yaml
type: Opaque
stringData:
  root-password: <pw>
  dbz-state-57-password: <pw>
  dbz-state-8-password: <pw>
```

Cada Deployment `debezium-server-<N>` lee solo la key que le corresponde:

```yaml
env:
  - name: DEBEZIUM_SOURCE_OFFSET_STORAGE_JDBC_PASSWORD
    valueFrom:
      secretKeyRef:
        name: debezium-state-credentials
        key: dbz-state-57-password    # o dbz-state-8-password según el stack
```

**Razones:**
- Un solo Secret para todo el state-store mantiene la simetría con "un solo state-store".
- Las keys explícitamente nombradas con sufijo hacen evidente qué password va a quién.

### Decisión 6 — Manifests organizados por directorio pero apuntando al mismo namespace

Los directorios `minikube/mysql5.7/` y `minikube/mysql8/` se conservan como organización lógica (es donde el lector busca "qué hay en el stack 5.7?"). Pero cada manifest declara `namespace: cdc-lab`. Se agrega un directorio nuevo `minikube/shared/`:

```
minikube/
├── mysql5.7/                              (manifests del stack 5.7, namespace=cdc-lab)
│   ├── 01-configmaps-57.yaml
│   ├── 02-secrets-57.yaml
│   ├── 03-mysql-primary-57.yaml
│   ├── 04-mysql-replica-57.yaml
│   ├── 05-cdc-sink-57.yaml
│   └── 06-debezium-server-57.yaml
├── mysql8/                                (idem stack 8)
│   └── ...-8.yaml
└── shared/                                (compartido por ambos stacks)
    ├── 00-namespace.yaml
    └── 04a-mysql-debezium-state.yaml
```

Los archivos `00-namespace.yaml` de cada stack se eliminan (el namespace ahora vive en `shared/`). Los archivos se renombran con sufijo `-57` / `-8` para hacer evidente a qué stack pertenecen (también ayuda cuando ambos directorios se navegan juntos).

### Decisión 7 — Greenfield para los offsets

Igual que en `migrate-debezium-state-to-mysql`: no hay migrator de offsets viejos. Al apuntar Debezium al state-store nuevo (con las DBs vacías), arrancará `snapshot.mode=initial` y re-snapshoteará `inventory.customers`. Aceptable en el lab.

### Decisión 8 — Scripts de RTO con selector de label

`rto_measure.py` actualmente asume:
- namespace pasado como arg
- label fijo `app=debezium-server` para localizar el pod
- label fijo `app=cdc-sink` para el sink

Tras este change ambos Debezium viven en el mismo namespace, así que `app=debezium-server` matchea dos pods. El script tiene que aceptar un **label-selector adicional**. Llamada:

```bash
python3 rto_measure.py cdc-lab 3 mysql8-auto --pod-label-selector "app=debezium-server,stack=mysql8" --sink-label-selector "app=cdc-sink,stack=mysql8"
```

Los defaults siguen siendo `app=debezium-server` y `app=cdc-sink` (compatible con el uso pre-consolidación si se quiere correr contra el lab viejo).

`rto_experiment.sh` se actualiza para invocar `rto_measure.py` con los labels correctos por stack, y la tabla resumen reporta por label en lugar de por namespace.

### Decisión 9 — Orden de migración

La consolidación es destructiva (borra los namespaces viejos). El orden seguro:

1. Crear `cdc-lab` y todos los recursos del nuevo lab. Esperar que estén Ready.
2. Validar funcionalmente (snapshot inicial, sink recibiendo eventos, RTO experiment OK).
3. **Solo entonces** borrar `cdc-mysql57` y `cdc-mysql8`.

Si el paso 2 falla, los namespaces viejos siguen ahí y el lab anterior funciona — se puede revertir borrando `cdc-lab` y dejando los viejos.

## Risks / Trade-offs

- **[Riesgo] El re-snapshot es visible al consumidor del sink.** Mitigación: documentado como evento operativo. El consumidor de paridad ya conoce este escenario por `migrate-debezium-state-to-mysql`.
- **[Riesgo] Sufijo `-57` en los manifests rompe `git blame` / `git log --follow` para los archivos renombrados.** Mitigación: usar `git mv` y commitear el rename solo, sin cambios funcionales, para preservar historia. Tasks.md lo refleja.
- **[Riesgo] Los scripts y Makefile actualizados son incompatibles con el lab pre-consolidación.** Mitigación: aceptable; el cutover es one-way (los namespaces viejos se borran al cierre del change).
- **[Trade-off] El namespace único acopla el lifecycle de los dos stacks.** `kubectl delete namespace cdc-lab` mata ambos. Aceptado: en el lab, eso es lo que se espera. Para borrar solo un stack: `kubectl delete -f minikube/mysql5.7/`.

## Migration Plan

1. **Preparación:** asegurar que el lab actual (post `migrate-debezium-state-to-mysql`) está sano y los offsets están al día.
2. **Crear nuevo namespace y state-store:**
   - `kubectl apply -f minikube/shared/00-namespace.yaml`
   - `kubectl apply -f minikube/shared/04a-mysql-debezium-state.yaml`
   - `kubectl rollout status deployment/mysql-debezium-state -n cdc-lab --timeout=180s`
3. **Aplicar stack 5.7 en `cdc-lab`:**
   - `kubectl apply -f minikube/mysql5.7/` (todos los manifests apuntan a `cdc-lab` ya)
   - Esperar a que `mysql-primary-57`, `mysql-replica-57`, `cdc-sink-57`, `debezium-server-57` queden Ready.
4. **Aplicar stack 8 en `cdc-lab`:** idem con sus manifests.
5. **Validar funcionalmente** (snapshot inicial completado, `dbz_state_57.offset_storage` y `dbz_state_8.offset_storage` con filas, sink recibiendo POSTs).
6. **Re-experimento RTO** con `minikube/scripts/rto_experiment.sh 3` para regresión.
7. **Cutover:** borrar `cdc-mysql57` y `cdc-mysql8` (`kubectl delete namespace ...`). El lab queda solo en `cdc-lab`.

## Open Questions

- ¿El nombre `cdc-lab` es definitivo o se prefiere otro (e.g., `cdc`, `debezium-lab`, `withreplica`)? Cambio trivial pre-aplicación; basta con `sed -i 's/cdc-lab/<nuevo>/g'` sobre los manifests nuevos.
- ¿`debezium.source.database.server.id` (actualmente 42 en mysql57 y 43 en mysql8) sigue siendo válido con ambos en el mismo namespace? Sí — `server.id` es para MySQL, no para Kubernetes; importa solo que los dos Debezium no compartan id. Como `mysql-replica-57` y `mysql-replica-8` son MySQL distintos, el server.id puede repetirse, pero por convención los mantenemos distintos.
- ¿Se conserva la URL JDBC con `?useSSL=false` o se habilita SSL en el state-store? Mantenerlo igual que ahora (`useSSL=false`) para no introducir cambio adicional. SSL en el state-store es alcance de otro change si se necesita.
