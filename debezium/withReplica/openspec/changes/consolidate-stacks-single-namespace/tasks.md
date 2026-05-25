## 0. Inventario de archivos involucrados

Esta sección es referencia, no tareas accionables. Describe qué función cumple cada archivo que este change **crea**, **modifica**, **mueve** o **elimina**.

### Archivos nuevos (creados)

- **`minikube/shared/00-namespace.yaml`** — declara el namespace único `cdc-lab` que reemplaza a `cdc-mysql57` + `cdc-mysql8`.
- **`minikube/shared/04a-mysql-debezium-state.yaml`** — el único `mysql-debezium-state` (PVC + ConfigMap initdb + Secret + Service + Deployment) compartido por ambos stacks. Reemplaza los dos `04a-mysql-debezium-state.yaml` per-stack.

### Archivos modificados (renombrado + edición de namespace + nombres con sufijo)

Cada archivo cambia tres cosas: (a) `namespace` pasa a `cdc-lab`, (b) los nombres de recursos y sus referencias toman sufijo `-57` o `-8`, (c) los `metadata.labels.stack` se agregan a todos los recursos del stack.

- **`minikube/mysql5.7/00-namespace.yaml`** → **eliminado**. El namespace ahora vive en `minikube/shared/00-namespace.yaml`.
- **`minikube/mysql5.7/01-configmaps.yaml`** → **renombrado a `01-configmaps-57.yaml`**. ConfigMaps internos: `mysql-primary-config` → `mysql-primary-config-57`, `mysql-primary-initdb` → `mysql-primary-initdb-57`, `mysql-replica-config` → `mysql-replica-config-57`, `mysql-replica-initdb` → `mysql-replica-initdb-57`, `mysql-replica-healthcheck` → `mysql-replica-healthcheck-57`, `debezium-config` → `debezium-config-57`. Dentro del `debezium-config-57`: `database.hostname` pasa de `mysql-replica` a `mysql-replica-57`; las JDBC URLs del state-store pasan de `mysql-debezium-state:3306/dbz_state` a `mysql-debezium-state:3306/dbz_state_57`; el usuario JDBC pasa de `dbz_state` a `dbz_state_57`.
- **`minikube/mysql5.7/02-secrets.yaml`** → **renombrado a `02-secrets-57.yaml`**. Secret `mysql-credentials` → `mysql-credentials-57`. **Se elimina** del archivo el Secret `debezium-state-credentials` (ahora vive único en `minikube/shared/04a-...yaml`).
- **`minikube/mysql5.7/03-mysql-primary.yaml`** → **renombrado a `03-mysql-primary-57.yaml`**. StatefulSet `mysql-primary` → `mysql-primary-57`; Services `mysql-primary` y `mysql-primary-nodeport` → `mysql-primary-57` y `mysql-primary-nodeport-57`. Referencias internas a `mysql-primary-config` y `mysql-primary-initdb` actualizadas.
- **`minikube/mysql5.7/04-mysql-replica.yaml`** → **renombrado a `04-mysql-replica-57.yaml`**. StatefulSet `mysql-replica` → `mysql-replica-57`; Service idem. La env var que pasa el hostname del primary cambia a `mysql-primary-57`.
- **`minikube/mysql5.7/05-cdc-sink.yaml`** → **renombrado a `05-cdc-sink-57.yaml`**. Deployment `cdc-sink` → `cdc-sink-57`; Service idem.
- **`minikube/mysql5.7/06-debezium-server.yaml`** → **renombrado a `06-debezium-server-57.yaml`**. Deployment `debezium-server` → `debezium-server-57`. Env var `DEBEZIUM_SOURCE_*_JDBC_PASSWORD` ahora referencia `secretKeyRef.name=debezium-state-credentials` (único en `cdc-lab`) y `key=dbz-state-57-password`. La URL del sink en `debezium-config-57` apunta a `cdc-sink-57:8080`.
- **`minikube/mysql5.7/04a-mysql-debezium-state.yaml`** → **eliminado**. Reemplazado por `minikube/shared/04a-mysql-debezium-state.yaml`.
- **`minikube/mysql8/00-namespace.yaml`** → **eliminado** (mismo motivo que el del 5.7).
- **`minikube/mysql8/01-configmaps.yaml`** ... **`minikube/mysql8/06-debezium-server.yaml`** → idénticas transformaciones a las del 5.7 pero con sufijo `-8`, namespace `cdc-lab`, DB `dbz_state_8`, usuario `dbz_state_8`, password key `dbz-state-8-password`.
- **`minikube/mysql8/04a-mysql-debezium-state.yaml`** → **eliminado**.

### Scripts e infraestructura modificada

- **`minikube/Makefile`**: targets `up-5.7` y `up-8` ahora aplican el namespace compartido primero, luego el state-store, luego sus respectivos directorios. `wait-healthy-*` y `ps-*` cambian a usar `-l stack=mysql57` / `stack=mysql8` en lugar de `-n`. `down-5.7` y `down-8` se reescriben para borrar por label, no por namespace. Se agrega un nuevo target `down` que borra todo el namespace `cdc-lab` en un paso.
- **`minikube/scripts/rto_measure.py`**: nuevo arg opcional `--pod-label-selector` (default `app=debezium-server`) y `--sink-label-selector` (default `app=cdc-sink`). El namespace pasa a ser `cdc-lab` siempre que se invoque post-consolidación.
- **`minikube/scripts/rto_experiment.sh`**: la constante `STACKS` ahora es `("57:mysql5.7" "8:mysql8")` y el script invoca `rto_measure.py cdc-lab N <label> --pod-label-selector app=debezium-server,stack=mysql<N> --sink-label-selector app=cdc-sink,stack=mysql<N>`. La tabla resumen reporta por stack (label), no por namespace.
- **`minikube/scripts/loadgen-long.yaml`**: el placeholder `__NAMESPACE__` se reemplaza siempre por `cdc-lab`; se agrega un placeholder `__STACK_LABEL__` (`57` o `8`) que el script usa para el nombre del Job (`load-long-57` / `load-long-8`) y la label `stack`.
- **`minikube/load-generator/job-mysql5.7.yaml`** y **`minikube/load-generator/job-mysql8.yaml`**: namespace a `cdc-lab`, nombres con sufijo, label `stack`.

### Archivos no tocados

- `minikube/images/debezium-server-mysql57-jdbc/Dockerfile` — la imagen no cambia.
- `docker-compose/` — fuera de alcance (este change solo toca minikube).

## 1. Pre-condición

- [x] 1.1 Confirmar que `migrate-debezium-state-to-mysql` está archivado (o sus manifests aplicados). Es la baseline desde la que parte este change.
- [x] 1.2 Snapshot del estado del lab actual: `kubectl get all,pvc,cm,secrets -n cdc-mysql57 > /tmp/snapshot-57-pre.txt` y lo mismo para `cdc-mysql8`. Útil si hay que comparar después del cutover.
- [x] 1.3 Confirmar que minikube tiene suficiente memoria/CPU para correr en paralelo ambos labs (el viejo y el nuevo) durante la transición. Si no, parar el viejo primero (decisión consciente: pierde la red de seguridad de rollback rápido).

## 2. Crear directorio `shared/` con namespace y state-store

- [x] 2.1 Crear `minikube/shared/00-namespace.yaml` con `kind: Namespace`, `metadata.name: cdc-lab`, `metadata.labels: {lab: withreplica}`.
- [x] 2.2 Crear `minikube/shared/04a-mysql-debezium-state.yaml` con:
  - `PersistentVolumeClaim debezium-state-data` (`ReadWriteOnce`, 1Gi — un poco más que el per-stack porque ahora soporta dos DBs).
  - `Secret debezium-state-credentials` con keys `root-password`, `dbz-state-57-password`, `dbz-state-8-password` (passwords generados con `openssl rand -base64 32`).
  - `ConfigMap mysql-debezium-state-initdb` con un único `00-schema.sql` que:
    - Crea las dos DBs `dbz_state_57` y `dbz_state_8`.
    - Crea los dos usuarios `dbz_state_57` y `dbz_state_8` con `IDENTIFIED WITH mysql_native_password BY '<placeholder>'`.
    - Otorga `GRANT SELECT, INSERT, UPDATE, DELETE, CREATE ON dbz_state_57.* TO 'dbz_state_57'@'%'` y simétricamente para el 8.
    - Crea en cada DB las tablas `offset_storage` y `schema_history` con el esquema validado en `migrate-debezium-state-to-mysql` (usar `MEDIUMTEXT` para `history_data`, PK explícito en ambas).
  - Un segundo entry del initdb (`01-set-passwords.sh`) que hace dos `ALTER USER ... IDENTIFIED WITH mysql_native_password BY '${ENV}'` (uno por usuario) con los passwords reales tomados de env vars `DBZ_STATE_57_PASSWORD` y `DBZ_STATE_8_PASSWORD`.
  - `Service mysql-debezium-state` (ClusterIP, port 3306).
  - `Deployment mysql-debezium-state` con imagen `mysql:8.0` (la versión más nueva da más margen de compatibilidad), probes idénticas a las del state-store por-stack, env vars `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE=mysql` (placeholder; las DBs reales las crea el initdb), `DBZ_STATE_57_PASSWORD`, `DBZ_STATE_8_PASSWORD`.
- [x] 2.3 `kubectl --dry-run=client apply -f minikube/shared/00-namespace.yaml` y idem para el state-store. Corregir errores de formato.

## 3. Renombrar y reescribir manifests del stack 5.7

- [x] 3.1 `git mv minikube/mysql5.7/01-configmaps.yaml minikube/mysql5.7/01-configmaps-57.yaml` (y todos los demás 03–06 con `git mv` para preservar historia).
- [x] 3.2 `git rm minikube/mysql5.7/00-namespace.yaml` y `git rm minikube/mysql5.7/04a-mysql-debezium-state.yaml`.
- [x] 3.3 Editar cada archivo renombrado: cambiar `namespace: cdc-mysql57` a `namespace: cdc-lab`. Agregar `stack: mysql57` a todos los `metadata.labels`. Renombrar recursos con sufijo `-57` (StatefulSets, Services, Deployments, ConfigMaps, Secrets). Actualizar todas las referencias internas (`selector.matchLabels`, `volumeClaimTemplates`, `configMapRef`/`secretRef`, hostnames en env vars y propiedades).
- [x] 3.4 En `06-debezium-server-57.yaml`: env vars `DEBEZIUM_SOURCE_OFFSET_STORAGE_JDBC_PASSWORD` y `DEBEZIUM_SOURCE_SCHEMA_HISTORY_INTERNAL_JDBC_PASSWORD` ahora apuntan a `secretKeyRef.name=debezium-state-credentials` (único) y `key=dbz-state-57-password`.
- [x] 3.5 En `01-configmaps-57.yaml` ConfigMap `debezium-config-57`: cambiar `debezium.source.database.hostname` a `mysql-replica-57`; cambiar las JDBC URLs a `jdbc:mysql://mysql-debezium-state:3306/dbz_state_57?useSSL=false`; cambiar el `jdbc.user` a `dbz_state_57`; cambiar el sink URL a `http://cdc-sink-57:8080`.
- [x] 3.6 Validar `kubectl --dry-run=client apply -f minikube/mysql5.7/`.

## 4. Renombrar y reescribir manifests del stack 8

- [x] 4.1 Repetir 3.1–3.6 para `minikube/mysql8/`, con sufijo `-8`, DB `dbz_state_8`, usuario `dbz_state_8`, password key `dbz-state-8-password`, sink URL `http://cdc-sink-8:8080`.

## 5. Actualizar load-generator

- [x] 5.1 Modificar `minikube/load-generator/job-mysql5.7.yaml`: namespace a `cdc-lab`, nombre del Job pasa a `load-mysql5.7-57-`, label `stack: mysql57`, env var `MYSQL_HOST` ahora `mysql-primary-57`.
- [x] 5.2 Modificar `minikube/load-generator/job-mysql8.yaml` análogo.
- [x] 5.3 Modificar `minikube/scripts/loadgen-long.yaml`: el placeholder `__NAMESPACE__` ahora siempre será `cdc-lab` cuando se use post-consolidación; agregar `__STACK_LABEL__` (`57` o `8`) para el nombre del Job (`load-long-57` / `load-long-8`) y la label `stack`.

## 6. Actualizar Makefile

- [x] 6.1 Cambiar las variables `NS57` y `NS8` por una constante única `NS := cdc-lab`. Agregar `STACK_57 := mysql57` y `STACK_8 := mysql8` para los labels.
- [x] 6.2 Reescribir `up`:
  ```
  up: image-load-57 image-load
  	kubectl apply -f minikube/shared/
  	kubectl rollout status deployment/mysql-debezium-state -n cdc-lab --timeout=180s
  	kubectl apply -f minikube/mysql5.7/
  	kubectl apply -f minikube/mysql8/
  ```
- [x] 6.3 Reescribir `up-5.7` para aplicar solo el namespace + state-store si no existe, luego solo su directorio. Idem `up-8`.
- [x] 6.4 Reescribir `wait-healthy-5.7`, `ps-5.7`, `logs-sink-5.7`, `load-5.7` usando `-n cdc-lab -l stack=mysql57`. Idem para `-8`.
- [x] 6.5 Reescribir `down` para borrar el namespace `cdc-lab` entero. `down-5.7` y `down-8` se reescriben para borrar por label (`kubectl delete all,cm,secrets -n cdc-lab -l stack=mysql57`), no por namespace.

## 7. Actualizar scripts de RTO

- [x] 7.1 Modificar `minikube/scripts/rto_measure.py`: agregar args `--pod-label-selector` (default `app=debezium-server`) y `--sink-label-selector` (default `app=cdc-sink`). Reemplazar las constantes `DEBEZIUM_POD_LABEL_SELECTOR` y `SINK_POD_LABEL_SELECTOR` por los argumentos. `python3 -m py_compile` debe pasar.
- [x] 7.2 Modificar `minikube/scripts/rto_experiment.sh`: la constante `STACKS` pasa a `("57:mysql5.7" "8:mysql8")`. La función `run_measurements_for_stack` invoca `rto_measure.py cdc-lab N <stack_label_short>-auto --pod-label-selector "app=debezium-server,stack=mysql<N>" --sink-label-selector "app=cdc-sink,stack=mysql<N>"`. `deploy_long_load_generator` ahora siempre apunta a `cdc-lab` y agrega `__STACK_LABEL__` en el sed.
- [x] 7.3 `bash -n minikube/scripts/rto_experiment.sh` y `python3 -m py_compile minikube/scripts/rto_measure.py` deben pasar.

## 8. Aplicar y verificar

- [x] 8.1 `kubectl apply -f minikube/shared/`. Esperar `kubectl rollout status deployment/mysql-debezium-state -n cdc-lab --timeout=180s`.
- [x] 8.2 Verificar que las dos DBs y los dos usuarios existen:
  ```
  ROOT=$(kubectl get secret -n cdc-lab debezium-state-credentials -o jsonpath='{.data.root-password}' | base64 -d)
  kubectl exec -n cdc-lab deploy/mysql-debezium-state -- mysql -uroot -p"$ROOT" -e \
    "SHOW DATABASES; SELECT user, plugin FROM mysql.user WHERE user LIKE 'dbz_state%';"
  ```
- [x] 8.3 `kubectl apply -f minikube/mysql5.7/`. Esperar a que `mysql-primary-57`, `mysql-replica-57`, `cdc-sink-57`, `debezium-server-57` queden Ready (puede haber latency mientras debezium-server-57 hace su snapshot inicial).
- [x] 8.4 `kubectl apply -f minikube/mysql8/`. Idem con sus pods.
- [x] 8.5 `kubectl get pods -n cdc-lab -o wide` y confirmar 9 pods (4 MySQL + 2 sink + 2 Debezium + 1 state-store), todos Ready.
- [x] 8.6 Verificar que los offsets se están persistiendo en las DBs correctas:
  ```
  kubectl exec -n cdc-lab deploy/mysql-debezium-state -- mysql -uroot -p"$ROOT" -e \
    "SELECT COUNT(*) FROM dbz_state_57.offset_storage;
     SELECT COUNT(*) FROM dbz_state_8.offset_storage;
     SELECT COUNT(*) FROM dbz_state_57.schema_history;
     SELECT COUNT(*) FROM dbz_state_8.schema_history;"
  ```
- [x] 8.7 Verificar aislamiento: intentar conectarse con el usuario `dbz_state_57` y leer de `dbz_state_8`:
  ```
  PW57=$(kubectl get secret -n cdc-lab debezium-state-credentials -o jsonpath='{.data.dbz-state-57-password}' | base64 -d)
  kubectl exec -n cdc-lab deploy/mysql-debezium-state -- mysql -u dbz_state_57 -p"$PW57" -e "SELECT * FROM dbz_state_8.offset_storage;"
  # → debe fallar con "command denied"
  ```

## 9. Re-medición RTO (regresión)

- [x] 9.1 Aplicar load-generators: `minikube/scripts/rto_experiment.sh 3` (que ya internamente crea los load-gens correctos).
- [x] 9.2 Comparar la mediana de TTR y TTFE contra la baseline post-`migrate-debezium-state-to-mysql` (mysql57: 22.37s / 6.28s; mysql8: 22.32s / 5.90s). Esperado: sin degradación significativa (±10%).
- [x] 9.3 Verificar no-duplicación: el consumidor del sink no recibe eventos cuyo offset previo al delete sea reemitido en ninguna corrida.

## 10. Cutover (destructivo)

- [x] 10.1 Confirmar que `cdc-lab` está sano funcionalmente (todos los pods Ready, sink recibiendo, offsets avanzando, RTO en rango).
- [x] 10.2 `kubectl delete namespace cdc-mysql57 --wait` (puede tomar minutos por los Pods con PVC).
- [x] 10.3 `kubectl delete namespace cdc-mysql8 --wait`.
- [x] 10.4 Confirmar que el sink consumidor sigue procesando solo eventos del nuevo namespace (no hay endpoints colgados del viejo).

## 11. Documentación

- [x] 11.1 Crear `openspec/changes/consolidate-stacks-single-namespace/runbook.md` con bitácora paso a paso del cutover, comandos `kubectl` exactos, output relevante, RTO resultante, y anexo de troubleshooting (qué hacer si el state-store no arranca, qué pasa si los grants no se aplican, cómo verificar aislamiento por usuario).
- [x] 11.2 Documentar en `runbook.md` el procedimiento de **rollback**: revertir el commit que aplica este change, re-aplicar los manifests viejos (vuelven a crear `cdc-mysql57` y `cdc-mysql8`), borrar `cdc-lab`. Aceptable que el rollback implique re-snapshot.

## 12. Cierre

- [x] 12.1 `openspec validate consolidate-stacks-single-namespace --type change --strict` y corregir errores de formato.
- [x] 12.2 Marcar listo para archivar.
