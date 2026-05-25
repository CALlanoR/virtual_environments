## Context

`evaluate-debezium-server-ha` dejó la configuración actual estable y medida: `debezium-server` con `replicas: 1`, `strategy: Recreate`, probes mínimas (httpGet a `/q/health/{live,ready}`) y persistencia de offset (`/debezium/data/offsets.dat`) y schema history (`/debezium/data/schema-history.dat`) en un PVC `debezium-data` (`ReadWriteOnce`, 100Mi).

El usuario aclaró que en producción la base de datos vive fuera de Kubernetes, **el primary es de solo-lectura para Debezium** (constraint del DBA: no se aceptan escrituras desde herramientas CDC), y `mysql-replica` tiene `read_only = ON` además de que el usuario `debezium` no tiene los privilegios para saltárselo. Por lo tanto, **el offset no puede vivir ni en el primary ni en el replica**, y la única opción viable es una base de datos pequeña dedicada al state de Debezium.

Inspección de las imágenes Debezium del lab (`2026-05-14`):

| Stack | Imagen | Debezium server | `debezium-storage-jdbc` shipped | Driver |
|---|---|---|---|---|
| `cdc-mysql8` | `withreplica/debezium-server-mysql:3.5.0.Final` (custom) | 3.5.0.Final | ✅ `debezium-storage-jdbc-3.5.0.Final.jar` | `mysql-connector-j-8.3.0.jar` |
| `cdc-mysql57` | `debezium/server:2.4.2.Final` (oficial) | 2.4.2.Final | ❌ no incluido | `mysql-connector-j-8.0.33.jar` |

El stack 8 puede usar JDBC backing store as-is. El stack 5.7 necesita una imagen custom que agregue ese JAR.

## Goals / Non-Goals

**Goals:**
- Mover `offset.storage` y `schema.history.internal` de `File*` a `Jdbc*` en ambos stacks.
- Desplegar un MySQL dedicado por stack (`mysql-debezium-state`) con la mínima superficie operativa razonable (1 réplica, PVC chico, usuario con privilegios CRUD acotados).
- Mantener el aislamiento del path CDC: el state-store **no** está en la lista de captura de Debezium y vive en un host distinto que la fuente, garantizando que las escrituras de offset no se autoconsuman.
- Mantener el RTO actual o mejorarlo.

**Non-Goals:**
- Compartir un único `mysql-debezium-state` entre ambos stacks (cross-namespace). Cada stack es autocontenido por diseño existente; mantenemos el invariante.
- Migrar el offset existente del PVC viejo al nuevo store. Greenfield: aceptar un re-snapshot de `inventory.customers`. Trivial en el lab; fuera de scope un migrator real.
- Upgrade del stack mysql5.7 a Debezium 3.x. Mantener 2.4.2 y compensar con imagen custom.
- Cambiar replicas/strategy/probes del Deployment `debezium-server`. Esos fueron alcance de `evaluate-debezium-server-ha`.
- HA del propio `mysql-debezium-state`. Es 1 réplica como cualquier otro MySQL del lab; si se cae, Debezium no puede flushear offset hasta que vuelva (riesgo aceptado y documentado).

## Decisions

### Decisión 1 — Una `mysql-debezium-state` **por stack**

**Elegido:** un Deployment por namespace. Cada stack ya es autocontenido (`mysql-primary`, `mysql-replica`, `cdc-sink`, `debezium-server` por separado). Agregar un sexto componente per-stack respeta el patrón. Borrar un stack borra su state. Cero acoplamiento cross-namespace.

**Alternativa descartada:** un `mysql-debezium-state` compartido en un namespace tercero (p.ej. `cdc-shared`). Beneficio: una DB menos. Coste: cross-namespace DNS, RBAC adicional, y romper la propiedad "un stack es un namespace". El beneficio no compensa.

### Decisión 2 — Imagen custom para mysql5.7 sin upgrade de Debezium

**Elegido:** crear `withreplica/debezium-server-mysql57-jdbc:2.4.2.Final` que extiende `debezium/server:2.4.2.Final` y agrega `debezium-storage-jdbc-2.4.2.Final.jar` (descargado de Maven Central durante el build).

**Razones:**
- Cambio mínimo, contenido (~5 líneas de Dockerfile).
- No requiere validar compatibilidad de la versión 3.x del conector MySQL contra MySQL 5.7.
- Mantiene el lab como sandbox honesto del path productivo legacy (si en prod se sigue usando 2.4 contra MySQL 5.7, este es el mismo escenario).

**Alternativa descartada:** upgrade a 3.x. Implicaría re-validar todo el comportamiento del conector contra MySQL 5.7, fuera del alcance de este change.

### Decisión 3 — Migrar offset **y** schema history (no solo offset)

**Elegido:** migrar ambos a JDBC. Tras el cambio, el PVC `debezium-data` queda vacío y se puede eliminar.

**Razones:**
- Si dejamos schema history en file, conservamos el PVC `ReadWriteOnce` y todas sus desventajas (atadura al nodo, no consultable, etc.). No habríamos resuelto el problema.
- `debezium-storage-jdbc` provee ambas implementaciones (`JdbcOffsetBackingStore` y `JdbcSchemaHistory`). Migrar las dos juntas no cuesta más que migrar una.

### Decisión 4 — Greenfield (no migración del offset existente)

**Elegido:** al apuntar a la nueva DB vacía, Debezium dispara un snapshot inicial nuevo de `inventory.customers`. No se migra el `offsets.dat` viejo.

**Razones:**
- En el lab, `inventory.customers` tiene ~decenas de filas y el snapshot toma segundos.
- Escribir un migrator (parsear el binario de Kafka Connect file offsets, traducir al esquema de la tabla `offset_storage`, validar) es trabajo de varias horas para un beneficio cero en el lab.
- Para producción habrá que escribir el migrator a mano o usar la herramienta oficial de Debezium si existe; ese trabajo se hace fuera de este change.

**Aceptado conscientemente:** el sink recibirá eventos `op=r` (read) del snapshot inicial tras la migración. El consumidor de paridad primary↔replica tiene que tolerarlos o se filtran upstream.

### Decisión 5 — Usuario y privilegios

**Elegido:** crear un usuario `dbz_state` con `GRANT SELECT, INSERT, UPDATE, DELETE ON dbz_state.* TO 'dbz_state'@'%'`. Sin `CREATE` ni `DROP` post-bootstrap: las tablas las crea el initdb del MySQL del state-store, no Debezium.

**Razones:**
- Privilegio mínimo.
- Tablas pre-creadas con esquema fijo evita que Debezium ejecute DDL en runtime (más auditable).
- El usuario `root` (para administración) tiene su password en `02-secrets.yaml` igual que los otros MySQL del lab.

### Decisión 6 — Aislamiento del path CDC

**Elegido:** el `mysql-debezium-state` es **otro host** distinto a `mysql-primary` y `mysql-replica`. Debezium escribe ahí. El binlog de `mysql-replica` (que Debezium consume) **no** contiene esas escrituras porque vienen de otra instancia. Aislamiento por arquitectura, no por filtros.

Como defensa en profundidad, la config de Debezium **no** lista `dbz_state` en `database.include.list` (sigue siendo solo `inventory`).

### Decisión 7 — Tablas pre-creadas en el initdb

**Elegido:** el ConfigMap `mysql-debezium-state-initdb` crea las tablas vacías `offset_storage` y `schema_history`. El esquema fue verificado en Task 1.1 inspeccionando las clases `JdbcOffsetBackingStoreConfig` y `JdbcSchemaHistoryConfig` de los JAR `debezium-storage-jdbc-2.4.2.Final` y `3.5.0.Final`. Resultado: ambos esquemas son **casi idénticos**, solo difieren en si el `PRIMARY KEY` está declarado o no. Pre-creamos con PK explícito (compatible con ambas versiones) → **un solo `initdb` sirve para ambos stacks**.

```sql
CREATE TABLE offset_storage (
  id                 VARCHAR(36)    NOT NULL,
  offset_key         VARCHAR(1255),
  offset_val         VARCHAR(1255),
  record_insert_ts   TIMESTAMP      NOT NULL,
  record_insert_seq  INTEGER        NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;

CREATE TABLE schema_history (
  id                 VARCHAR(36)    NOT NULL,
  history_data       VARCHAR(65000),
  history_data_seq   INTEGER,
  record_insert_ts   TIMESTAMP      NOT NULL,
  record_insert_seq  INTEGER        NOT NULL,
  PRIMARY KEY (id, history_data_seq)
) ENGINE=InnoDB;
```

Las columnas siguen exactamente el `DEFAULT_TABLE_DDL` de Debezium (incluido `VARCHAR(65000)` para `history_data` y la nulabilidad de `offset_key` / `offset_val`). Los nombres `offset_storage` y `schema_history` **no** son los defaults de Debezium (`debezium_offset_storage` / `debezium_database_history`); por eso la config en Task 5.1 incluye `jdbc.offset.table.name=offset_storage` y `jdbc.schema.history.table.name=schema_history` para que Debezium use estos nombres en lugar de los suyos.

### Decisión 8 — Password vía Secret + env var

**Elegido:** el password del usuario `dbz_state` vive en un Secret `debezium-state-credentials` por namespace. El Deployment `debezium-server` lo expone como env var `DBZ_STATE_PASSWORD`. La config en `application.properties` lo referencia con `${env:DBZ_STATE_PASSWORD}` (Quarkus property substitution).

**Razones:**
- Patrón estándar en k8s.
- ConfigMaps no son secret-safe.
- Quarkus ya soporta `${env:VAR}` sin más.

## Risks / Trade-offs

- **[Riesgo] La caída de `mysql-debezium-state` deja a Debezium sin posibilidad de flushear offset.** Debezium fallaría las escrituras de checkpoint y eventualmente entraría en error. Mitigación: el state-store es 1 réplica con su PVC, así que la disponibilidad es similar a la del PVC actual; en operación normal el rate de escrituras de offset es bajo (cada `offset.flush.interval.ms=10000`, o sea, cada 10s). Si fuera un problema, se puede subir el grace period o agregar retries. No bloqueante para este change.
- **[Riesgo] El esquema de las tablas (`offset_storage`, `schema_history`) podría diferir entre Debezium 2.4 y 3.5.** Mitigación: `tasks.md` exige verificar el esquema esperado de cada versión contra el código de `debezium-storage-jdbc` antes de pre-crear las tablas. Si difieren, mantener dos `initdb` distintos por stack.
- **[Riesgo] El greenfield re-snapshot puede confundir al consumidor del sink.** Mitigación: documentar el cambio como "evento operativo" — el sink ve eventos `op=r` tras la migración. El consumidor que valida paridad primary↔replica ya tiene la decisión "tolerar duplicados durante operaciones programadas" o no; este change la fuerza a estar formalizada.
- **[Trade-off] Un componente más para mantener en cada stack.** Aceptado: el desacople vale más que la simplicidad de un PVC. Además, mover a producción quita el Deployment del state-store de la ecuación (la DB allá vive externa).
- **[Riesgo] La imagen custom para mysql5.7 introduce un punto de divergencia respecto a la imagen oficial.** Mitigación: el Dockerfile es mínimo (3 líneas) y reproducible; el Makefile incluye `image-build-57` por simetría con el existente `image-build`.

## Migration Plan

1. **Build de la imagen custom** para mysql5.7 (`make image-build-57 && make image-load-57`).
2. **Aplicar manifests por stack en orden:** primero los Secrets actualizados, después el `mysql-debezium-state` (espera a que esté `Ready`), después los ConfigMaps actualizados, finalmente el Deployment `debezium-server` modificado.
3. **Verificación funcional:** `kubectl exec` al pod `mysql-debezium-state` y `SELECT COUNT(*) FROM offset_storage` debería retornar > 0 segundos después del Ready de Debezium.
4. **Cleanup del PVC viejo:** `kubectl delete pvc debezium-data -n <namespace>` tras confirmar que Debezium ya no lo monta.
5. **Re-experimento RTO:** ejecutar `minikube/scripts/rto_experiment.sh 3` y validar que las medianas no se degradan respecto a la baseline.

## Open Questions

- ~~¿El esquema de tablas `offset_storage` y `schema_history` es 100% idéntico entre `debezium-storage-jdbc-2.4.2.Final` y `3.5.0.Final`?~~ **Resuelto en Task 1.1 (2026-05-14):** los esquemas son casi idénticos, solo difieren en la declaración de PRIMARY KEY (3.5.0 lo declara, 2.4.2 no). Pre-creando las tablas con PK explícito, un solo `initdb` sirve para ambos stacks. Esquema concreto en Decisión 7.
- ¿`offset.flush.interval.ms=10000` (10s) está bien para JDBC, o conviene subirlo? Cada flush ahora es una query, no un write a file. Por defecto 10s genera 6 queries/min — despreciable.
- ¿En producción, el `mysql-debezium-state` vive en el mismo cluster MySQL administrado que la fuente, en uno aparte, o en un servicio gestionado distinto? Decisión externa al lab; el contrato (DB dedicada con privilegios CRUD acotados) se mantiene en cualquier opción.
