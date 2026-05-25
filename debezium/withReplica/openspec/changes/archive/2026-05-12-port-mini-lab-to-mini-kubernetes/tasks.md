## 1. Scaffolding del directorio mini-kubernetes/

- [x] 1.1 Crear estructura `withReplica/mini-kubernetes/{mysql5.7,mysql8,load-generator}/` con `.gitkeep` donde sea necesario
- [x] 1.2 Crear `mini-kubernetes/README.md` placeholder (se rellena en bloque 7)
- [x] 1.3 Crear `mini-kubernetes/Makefile` placeholder con target `help` mínimo (se completa en bloque 6)

## 2. Imagen custom de Debezium 3.5

- [ ] 2.1 Verificar que `docker-compose/mysql8/debezium/Dockerfile` sigue construyendo `withreplica/debezium-server-mysql:3.5.0.Final` correctamente desde el host (`docker build -t withreplica/debezium-server-mysql:3.5.0.Final ./docker-compose/mysql8/debezium`)
- [ ] 2.2 Validar que `minikube image load withreplica/debezium-server-mysql:3.5.0.Final` deja la imagen visible en `minikube image ls`

## 3. Manifiestos del stack mysql5.7

- [x] 3.1 `mysql5.7/00-namespace.yaml` — Namespace `cdc-mysql57`
- [x] 3.2 `mysql5.7/02-secrets.yaml` — Secret `mysql-credentials` (root password, debezium password, repl password)
- [x] 3.3 `mysql5.7/01-configmaps.yaml` — ConfigMaps:
  - `mysql-primary-config` (contenido literal de `docker-compose/mysql5.7/mysql/primary/my.cnf`)
  - `mysql-primary-initdb` (`01-users.sql`, `02-demo-schema.sql` desde `docker-compose/mysql5.7/mysql/primary/init/`)
  - `mysql-replica-config` (`my.cnf` + `healthcheck.sh`, ambos desde `docker-compose/mysql5.7/mysql/replica/`)
  - `mysql-replica-initdb` (`01-start-replica.sql`)
  - `debezium-config` (`application.properties` desde `docker-compose/mysql5.7/debezium/conf/`)
- [x] 3.4 `mysql5.7/03-mysql-primary.yaml` — StatefulSet `mysql-primary` con `mysql:5.7`, command `--default-authentication-plugin=mysql_native_password`, volumeMounts para `/etc/mysql/conf.d/my.cnf` y `/docker-entrypoint-initdb.d/`, `volumeClaimTemplates` para `/var/lib/mysql`. Crea:
  - Service headless `mysql-primary-headless` para DNS estable del StatefulSet
  - Service ClusterIP `mysql-primary` (alias usado por la replica y por Debezium)
  - Service NodePort `mysql-primary-nodeport` con `nodePort: 30306`
- [x] 3.5 `mysql5.7/04-mysql-replica.yaml` — StatefulSet `mysql-replica` con:
  - `initContainer` `wait-for-primary`: imagen `mysql:5.7`, comando con loop `mysqladmin ping -h mysql-primary -uroot -p$MYSQL_ROOT_PASSWORD` hasta éxito
  - Container principal con healthcheck (readinessProbe + livenessProbe) ejecutando `/usr/local/bin/replica-healthcheck.sh` (montado desde ConfigMap, mode 0755)
  - Service headless, Service alias `mysql-replica`, Service NodePort `nodePort: 30307`
- [x] 3.6 `mysql5.7/05-cdc-sink.yaml` — Deployment `cdc-sink` con `mendhak/http-https-echo:40`, env `HTTP_PORT=8080`/`HTTPS_PORT=8443`, Service ClusterIP `cdc-sink:8080`
- [x] 3.7 `mysql5.7/06-debezium-server.yaml` — Deployment `debezium-server` con `debezium/server:2.4.2.Final`, volumeMount `/debezium/conf` desde ConfigMap `debezium-config`, PVC `debezium-data` montada en `/debezium/data`

## 4. Manifiestos del stack mysql8

- [x] 4.1 `mysql8/00-namespace.yaml` — Namespace `cdc-mysql8`
- [x] 4.2 `mysql8/02-secrets.yaml` — Secret `mysql-credentials`
- [x] 4.3 `mysql8/01-configmaps.yaml` — ConfigMaps equivalentes a los del bloque 3.3 pero desde `docker-compose/mysql8/...`
- [x] 4.4 `mysql8/03-mysql-primary.yaml` — StatefulSet `mysql:8.0`, sin `--default-authentication-plugin` (default 8.0 OK porque los users son creados con `mysql_native_password` en `01-users.sql`); Services con NodePort `30308`
- [x] 4.5 `mysql8/04-mysql-replica.yaml` — StatefulSet `mysql:8.0` con initContainer wait-for-primary, healthcheck (usando `Replica_*_Running`); Services con NodePort `30309`
- [x] 4.6 `mysql8/05-cdc-sink.yaml` — Deployment idéntico al del stack 5.7 (otro namespace)
- [x] 4.7 `mysql8/06-debezium-server.yaml` — Deployment con imagen `withreplica/debezium-server-mysql:3.5.0.Final`, `imagePullPolicy: IfNotPresent`, volumeMount `/debezium/config` (path 3.x, no `/debezium/conf`), PVC `debezium-data`

## 5. Load-generator

- [x] 5.1 `load-generator/configmap-script.yaml` — ConfigMap `load-generator-script` con `random_changes.py` y `requirements.txt` copiados literalmente desde `docker-compose/load-generator/`
- [x] 5.2 `load-generator/job-mysql5.7.yaml` — Job con `metadata.generateName: load-mysql5-7-` en namespace `cdc-mysql57`, `ttlSecondsAfterFinished: 300`, initContainer `pip-install` (imagen `python:3.12-slim`, `pip install -r /script/requirements.txt --target /deps`), container `load-generator` (imagen `python:3.12-slim`, env `PYTHONPATH=/deps`, command `python /script/random_changes.py --target mysql5.7 --host mysql-primary --port 3306`)
- [x] 5.3 `load-generator/job-mysql8.yaml` — equivalente con `--target mysql8` en namespace `cdc-mysql8`

## 6. Makefile

- [x] 6.1 Definir variables (`KUBECTL`, `NS57`, `NS8`, `IMG`)
- [x] 6.2 Target `help` con listado completo
- [x] 6.3 Targets `image-build` (`docker build -t $(IMG) ../docker-compose/mysql8/debezium`) y `image-load` (`minikube image load $(IMG)`)
- [x] 6.4 Targets `up-5.7`, `up-8` (este último depende de `image-load`), y `up` que ejecuta ambos
- [x] 6.5 Target `wait-healthy` usando `kubectl wait --for=condition=ready pod -l app=mysql-primary -n $(NS57) --timeout=300s` y equivalentes para los otros 3 Pods MySQL
- [x] 6.6 Targets `ps`, `logs-sink-5.7`, `logs-sink-8`
- [x] 6.7 Targets `load-5.7` y `load-8` (`kubectl apply -f load-generator/job-mysqlX.yaml`)
- [x] 6.8 Target `down` (`kubectl delete namespace $(NS57) $(NS8) --ignore-not-found`)

## 7. README

- [x] 7.1 Sección "Topología" con diagrama ASCII de los dos namespaces y sus pods
- [x] 7.2 Sección "Prerrequisitos": minikube ≥ 1.30, kubectl, make, addon `storage-provisioner` habilitado (default), `minikube start --cpus=4 --memory=6g` recomendado
- [x] 7.3 Sección "Diferencias con docker-compose" (tabla: namespaces, NodePorts 30306-30309, ConfigMaps en lugar de bind mounts, imagen custom load por `image-load`)
- [x] 7.4 Sección "Levantar": `make image-build && make image-load && make up && make wait-healthy`
- [x] 7.5 Sección "Verificar replicación" con `kubectl exec` ejemplos para ambos stacks
- [x] 7.6 Sección "Observar eventos CDC": `make logs-sink-5.7` y `make logs-sink-8`
- [x] 7.7 Sección "Generar carga": `make load-5.7` y `make load-8`; mencionar que cada invocación crea un Job nuevo y se auto-borra en 5 min
- [x] 7.8 Sección "Acceso desde el host": NodePort + `minikube service` y alternativa `kubectl port-forward`
- [x] 7.9 Sección "Limpieza": `make down`
- [x] 7.10 Sección "Troubleshooting" adaptada de `docker-compose/mysql5.7/README.md` y `mysql8/README.md` (replica no arranca, Debezium no se conecta, no veo eventos, imagen custom no encontrada)
- [x] 7.11 Nota explícita: el monitoreo (presente en `docker-compose/monitoring/`) queda fuera de alcance de esta variante

## 8. Validación funcional end-to-end

- [ ] 8.1 `make image-build && make image-load && make up && make wait-healthy` — sin errores, los 4 Pods MySQL Ready, ambos Debezium corriendo
- [ ] 8.2 `kubectl exec -n cdc-mysql57 mysql-replica-0 -- mysql -uroot -proot -e 'SHOW SLAVE STATUS\G' | grep -E 'Slave_(IO|SQL)_Running'` → ambos `Yes`
- [ ] 8.3 `kubectl exec -n cdc-mysql8 mysql-replica-0 -- mysql -uroot -proot -e 'SHOW REPLICA STATUS\G' | grep -E 'Replica_(IO|SQL)_Running'` → ambos `Yes`
- [ ] 8.4 `make load-8` en una terminal + `make logs-sink-8` en otra → se ven eventos `op=c/u/d` para `inventory.customers`, ninguno para `inventory.audit_log`
- [ ] 8.5 Repetir 8.4 para stack 5.7
- [ ] 8.6 Conectarse desde el host: `kubectl port-forward -n cdc-mysql8 svc/mysql-primary 13308:3306` y `mysql -h 127.0.0.1 -P 13308 -uroot -proot inventory -e 'SELECT COUNT(*) FROM customers'` → devuelve un número > 0
- [ ] 8.7 `make down` — ambos namespaces y sus PVCs son eliminados; un `make up` posterior arranca desde cero correctamente

## 9. Validación de la propuesta OpenSpec

- [x] 9.1 `openspec validate port-mini-lab-to-mini-kubernetes` pasa sin errores
- [x] 9.2 Revisión cruzada: cada Requirement del spec tiene al menos una Task que lo materializa
- [x] 9.3 Confirmar con el usuario antes de archivar (`openspec archive port-mini-lab-to-mini-kubernetes`) tras implementación
