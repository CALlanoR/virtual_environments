## MODIFIED Requirements

### Requirement: Probes mínimas presentes en ambos manifests

El Deployment `debezium-server` SHALL declarar `livenessProbe` y `readinessProbe` HTTP en ambos stacks (`cdc-mysql57` y `cdc-mysql8`) contra los endpoints Quarkus estándar (`/q/health/live` y `/q/health/ready`) en el puerto `8080`. El `readinessProbe.initialDelaySeconds` SHALL ser `5`, calibrado contra el `time-to-first-event` mediano (~5.5–6.1s) observado empíricamente en `evaluate-debezium-server-ha`, de modo que `Ready=True` se alinee con la disponibilidad funcional real y no quede artificialmente retrasado. El `livenessProbe.initialDelaySeconds` SHALL permanecer en `30` (asimetría de riesgo: un liveness kill prematuro es más costoso que un Ready demorado).

#### Scenario: readinessProbe.initialDelaySeconds en stack 5.7
- **WHEN** se inspecciona `minikube/mysql5.7/06-debezium-server.yaml`
- **THEN** el contenedor declara `readinessProbe.httpGet.path: /q/health/ready`, `readinessProbe.httpGet.port: 8080` y `readinessProbe.initialDelaySeconds: 5`

#### Scenario: readinessProbe.initialDelaySeconds en stack 8
- **WHEN** se inspecciona `minikube/mysql8/06-debezium-server.yaml`
- **THEN** el contenedor declara `readinessProbe.httpGet.path: /q/health/ready`, `readinessProbe.httpGet.port: 8080` y `readinessProbe.initialDelaySeconds: 5`

#### Scenario: livenessProbe sin cambios en ambos stacks
- **WHEN** se inspecciona el `livenessProbe` del contenedor principal en cualquiera de los dos manifests
- **THEN** declara `httpGet.path: /q/health/live`, `port: 8080`, `initialDelaySeconds: 30`, `periodSeconds: 15`, `failureThreshold: 4`

#### Scenario: startupProbe ausente
- **WHEN** se inspecciona el contenedor principal en cualquiera de los dos manifests
- **THEN** no declara `startupProbe`

## ADDED Requirements

### Requirement: Terminación ordenada con grace period suficiente para flush del offset

El Deployment `debezium-server` SHALL declarar `spec.template.spec.terminationGracePeriodSeconds: 60` en ambos stacks. Este valor da margen al proceso para responder a `SIGTERM`, hacer flush del offset al PVC `debezium-data` (`/debezium/data/offsets.dat`) y cerrar la conexión al binlog antes de que kubelet envíe `SIGKILL`. Es estrictamente necesario para garantizar que un shutdown ordenado no deje el offset truncado, lo que provocaría reprocesamiento de eventos al levantar el pod sustituto.

#### Scenario: terminationGracePeriodSeconds en stack 5.7
- **WHEN** se inspecciona `minikube/mysql5.7/06-debezium-server.yaml`
- **THEN** `spec.template.spec.terminationGracePeriodSeconds` está declarado y vale `60`

#### Scenario: terminationGracePeriodSeconds en stack 8
- **WHEN** se inspecciona `minikube/mysql8/06-debezium-server.yaml`
- **THEN** `spec.template.spec.terminationGracePeriodSeconds` está declarado y vale `60`

#### Scenario: Flush ordenado durante un rollout
- **WHEN** se ejecuta `kubectl rollout restart deployment/debezium-server -n <ns>` y kubelet envía `SIGTERM` al pod activo
- **THEN** Debezium dispone de hasta 60s para completar el flush del offset al PVC; al levantar el pod sustituto, el consumidor del sink no recibe eventos cuyo offset fuera ≤ al último confirmado antes del restart (es decir, no hay reprocesamiento inducido por shutdown abrupto)

### Requirement: Mejora del time-to-Ready verificada empíricamente

Tras aplicar este change, el sistema SHALL verificar mediante `minikube/scripts/rto_experiment.sh` (3 corridas por stack) que la mediana de `time_to_ready_seconds` baja al rango `[5, 12]` segundos, mejorando respecto a la baseline `[22.16, 22.24]` observada en `evaluate-debezium-server-ha`. La mediana de `time_to_first_event_seconds` SHALL mantenerse en `[5, 7]` segundos (sin regresión).

#### Scenario: time-to-Ready mediana mejorada
- **WHEN** se ejecuta `minikube/scripts/rto_experiment.sh 3` después de aplicar los manifests modificados
- **THEN** la mediana reportada de `time_to_ready_seconds` para cada stack está entre 5 y 12 segundos

#### Scenario: time-to-first-event sin regresión
- **WHEN** se ejecuta `minikube/scripts/rto_experiment.sh 3` después de aplicar los manifests modificados
- **THEN** la mediana reportada de `time_to_first_event_seconds` para cada stack está entre 5 y 7 segundos
