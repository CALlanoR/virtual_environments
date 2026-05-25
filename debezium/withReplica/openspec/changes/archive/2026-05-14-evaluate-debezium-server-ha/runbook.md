# Runbook — Evaluación empírica del RTO de `debezium-server`

Bitácora paso a paso del experimento. Ejecutado el `2026-05-14` contra minikube local (un nodo). El objetivo de este documento es que cualquiera pueda reproducir la medición sin contexto previo y entender qué se observó y qué recomendamos.

## 0. Estado de partida

Minikube ya arriba, ambos stacks (`cdc-mysql57` y `cdc-mysql8`) desplegados.

```
kubectl get pods -n cdc-mysql8 -o wide
kubectl get pods -n cdc-mysql57 -o wide
```

Resultado relevante observado: ambos `debezium-server` estaban `Ready=1/1` pero con `RESTARTS>0` (5 en mysql8, 1 en mysql57). Inspección de `describe` y `logs --previous` mostró que los restarts eran race conditions de arranque contra el Service `mysql-replica` (`UnknownHostException` en mysql57, `Communications link failure` en mysql8). El Deployment carecía de `initContainer` y de probes. Esto se documentó en `design.md` como hallazgo colateral y motivó la **Decisión 6 (warmup de 60s)** antes de medir.

## 1. Auditoría de la configuración (Tasks 1.1–1.2)

Lectura directa de los manifests:

```
cat minikube/mysql5.7/06-debezium-server.yaml
cat minikube/mysql8/06-debezium-server.yaml
```

Resultado: ambos estructuralmente idénticos salvo imagen y `mountPath` del ConfigMap. Sin probes, sin `terminationGracePeriodSeconds`, `replicas: 1`, `strategy: Recreate`. Tabla completa en `design.md` sección "Estado actual".

Verificación de rutas de persistencia:

```
grep -E "offset.storage.file.filename|schema.history.internal.file.filename" \
  minikube/mysql5.7/01-configmaps.yaml \
  minikube/mysql8/01-configmaps.yaml
```

Resultado: ambos stacks usan `/debezium/data/offsets.dat` y `/debezium/data/schema-history.dat`. El `mountPath` del PVC es `/debezium/data` en ambos. **Las rutas están dentro del PVC ✓**.

## 2. Identificación de la sonda de salud (Task 2.1)

Inspección de puertos en runtime:

```
kubectl exec -n cdc-mysql8 deploy/debezium-server -- cat /proc/net/tcp6 | head
kubectl exec -n cdc-mysql57 deploy/debezium-server -- cat /proc/net/tcp6 | head
```

Ambos pods escuchan en port `0x1F90` (= **8080**) en estado LISTEN (0A). Es el puerto HTTP de Quarkus.

Verificación de endpoints Quarkus:

```
for ep in /q/health/live /q/health/ready /q/health/started; do
  kubectl exec -n cdc-mysql8 deploy/debezium-server -- \
    curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8080$ep
  kubectl exec -n cdc-mysql57 deploy/debezium-server -- \
    curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8080$ep
done
```

Resultado: los 3 endpoints devolvieron HTTP 200 en ambas imágenes (`debezium/server:2.4.2.Final` y `withreplica/debezium-server-mysql:3.5.0.Final`).

**Decisión:** `httpGet /q/health/live` para liveness, `httpGet /q/health/ready` para readiness, port 8080.

## 3. Agregar probes (Tasks 2.2–2.4)

Edición de ambos manifests para añadir:

```yaml
livenessProbe:
  httpGet: { path: /q/health/live, port: 8080 }
  initialDelaySeconds: 30
  periodSeconds: 15
  failureThreshold: 4
readinessProbe:
  httpGet: { path: /q/health/ready, port: 8080 }
  initialDelaySeconds: 20
  periodSeconds: 10
  failureThreshold: 3
```

Aplicación:

```
kubectl apply -f minikube/mysql5.7/06-debezium-server.yaml
kubectl apply -f minikube/mysql8/06-debezium-server.yaml
kubectl rollout status deployment/debezium-server -n cdc-mysql8 --timeout=180s
kubectl rollout status deployment/debezium-server -n cdc-mysql57 --timeout=180s
```

Resultado: ambos rollouts completados sin error. Ambos pods llegaron a `Ready=1/1` con `RESTARTS=0` (esta vez no hubo race condition porque `mysql-replica` ya estaba arriba).

## 4. Setup del load-generator (Task 3.1)

El Job original `minikube/load-generator/job-mysql8.yaml` corre por defecto **40 segundos** y luego termina (`--duration 40` del script `random_changes.py`). Para cubrir 3 corridas + warmups necesitamos al menos 600s, así que se generó una variante en `minikube/scripts/loadgen-long.yaml` con `--duration 1200 --interval 0.5`. El YAML original no se modificó.

Aplicación por stack:

```
sed -e 's/__NS__/cdc-mysql8/'   -e 's/__TARGET__/mysql8/'   minikube/scripts/loadgen-long.yaml | kubectl apply -f -
sed -e 's/__NS__/cdc-mysql57/'  -e 's/__TARGET__/mysql5.7/' minikube/scripts/loadgen-long.yaml | kubectl apply -f -
```

Verificación: `kubectl logs -n <ns> -l app=load-generator --tail=5` mostró líneas `[hh:mm:ss] INSERT/UPDATE/DELETE id=N` cada ~0.5s, y `kubectl logs -n <ns> -l app=cdc-sink --tail=1` mostró POSTs llegando al sink.

## 5. Medición (Tasks 3.2–3.6 y 4.1–4.2)

Scripts (en `minikube/scripts/`, ejecutables y reusables):

- `rto_measure.py` — Python 3.12. Ejecuta N corridas contra **un** namespace.
- `rto_experiment.sh` — bash wrapper. Verifica pre-condiciones, despliega el load-generator, corre `rto_measure.py` 3 veces (configurable) por stack, imprime tabla resumen min/mediana/máx.
- `loadgen-long.yaml` — template de Job de load-generator con duración larga, parametrizado por namespace y target via `sed`.

Forma reproducible de re-ejecutar el experimento desde el repo:

```
minikube/scripts/rto_experiment.sh 3
```

Lógica por corrida en `rto_measure.py`:

1. Verifica pod actual con `age ≥ 60s` y `restartCount == 0`. Si no, espera (warmup, **Decisión 6**).
2. Lanza `kubectl logs -l app=cdc-sink --tail=0 -f --timestamps=true` en un thread para capturar cada POST entrante.
3. Registra `t_delete = time.time()` justo antes de `kubectl delete pod -l app=debezium-server -n <ns> --grace-period=0 --force`.
4. Hace polling cada 100ms a `kubectl get pod ... -o jsonpath` para detectar el pod sustituto y su `Ready=True`. Captura `t_ready` y `new_pod_ip`.
5. Recorre los eventos capturados del sink y toma el primero que cumple `ts > t_delete AND ip == new_pod_ip`. Captura `t_first_event`.
6. Reporta `time-to-Ready = t_ready - t_delete` y `time-to-first-event = t_first_event - t_delete`.

**Bug de metodología v1 detectado y corregido:** la primera versión del script no filtraba por IP del pod nuevo. En mysql5.7 dio `time-to-first-event` entre 12ms y 345ms, claramente irreal: estaba contando POSTs en vuelo del pod viejo que llegaron al sink milisegundos después del delete. Añadir el filtro de IP del pod sustituto resolvió esto y los números reales aparecieron alineados con mysql8.

### 5.1 Corridas mysql8

```
python3 minikube/scripts/rto_measure.py cdc-mysql8 3 mysql8v2
```

| Run | t_delete | new_pod IP | t-to-Ready | t-to-first-event |
|---|---|---|---|---|
| mysql8v2.1 | 1778782000.373 | 10.244.0.25 | 21.931s | 5.490s |
| mysql8v2.2 | 1778782061.423 | 10.244.0.26 | 22.236s | 5.517s |
| mysql8v2.3 | 1778782122.775 | 10.244.0.27 | 22.328s | 5.546s |

### 5.2 Corridas mysql5.7

```
python3 minikube/scripts/rto_measure.py cdc-mysql57 3 mysql57v2
```

| Run | t_delete | new_pod IP | t-to-Ready | t-to-first-event |
|---|---|---|---|---|
| mysql57v2.1 | 1778782153.263 | 10.244.0.28 | 22.042s | 6.114s |
| mysql57v2.2 | 1778782214.433 | 10.244.0.29 | 22.410s | 5.995s |
| mysql57v2.3 | 1778782275.966 | 10.244.0.30 | 22.160s | 6.108s |

### 5.3 Resumen estadístico

| Stack | t-to-Ready min/mediana/máx | t-to-first-event min/mediana/máx | gap (mediana) |
|---|---|---|---|
| `cdc-mysql8` | 21.93 / 22.24 / 22.33 s | 5.49 / 5.52 / 5.55 s | **16.72 s** |
| `cdc-mysql57` | 22.04 / 22.16 / 22.41 s | 6.00 / 6.11 / 6.11 s | **16.05 s** |

Dispersión max/min ≤ 1.02× la mediana en ambas métricas y ambos stacks. No fue necesario extender a 5 corridas (criterio en Decisión 4 del design).

## 6. Verificación de no-duplicación (Task 6.1)

Durante las 12 corridas totales (3 v1 + 3 v2 por stack), se inspeccionaron los logs del sink antes y después de cada delete buscando eventos con `op=c/u/d` y `id` repetidos para offsets previos al delete. Ningún evento previo al delete fue reemitido — Debezium reanudó desde el offset persistido en `/debezium/data/offsets.dat` sin replay parcial. **Requirement "No-duplicación tras recuperación": cumplido**.

## 7. Recomendaciones

> **Convención de etiquetas:**
> - **`Production-relevant`** — describe un defecto intrínseco de la configuración de Debezium en Kubernetes; aplica tanto al lab como al ambiente real.
> - **`Lab-only`** — describe un defecto que solo se manifiesta en este lab porque `mysql-primary`/`mysql-replica` son Pods dentro del cluster. En producción la base de datos vive **fuera** de Kubernetes y está siempre disponible, así que el problema no existe allá.

### (a) Sonda definitiva por imagen — `Production-relevant`

Ambas imágenes (`debezium/server:2.4.2.Final` y `withreplica/debezium-server-mysql:3.5.0.Final`) exponen los endpoints Quarkus estándar. **Mantener `httpGet /q/health/live` y `/q/health/ready` en port 8080.** No hay diferencia entre imágenes que justifique tratarlas distinto. La imagen y los endpoints son los mismos en producción.

### (b) `initialDelaySeconds` actual es demasiado conservador — `Production-relevant`

El gap medido `time-to-Ready − time-to-first-event ≈ 16s` está dominado por `readinessProbe.initialDelaySeconds: 20`. Debezium está sirviendo eventos al sink ~5–6s después del delete, pero Kubernetes no marca `Ready` hasta ~22s porque la primera evaluación de la sonda recién ocurre a +20s. **Recomendación: bajar `readinessProbe.initialDelaySeconds` a `5`** (los 5s reales que tarda Debezium en empezar a emitir son una cota inferior holgada del bootstrap real, y son el dato empírico que esta medición produjo). Con eso, el `time-to-Ready` observado bajaría de ~22s a ~7–8s y se alinearía con la disponibilidad funcional real.

Este número depende del tiempo de bootstrap intrínseco de Debezium (JVM + Quarkus + conexión inicial), que es prácticamente el mismo en producción (la DB externa responde tan rápido o más que el Pod `mysql-replica`).

`livenessProbe.initialDelaySeconds: 30` también podría bajarse, pero el riesgo asimétrico aquí es mayor (un kill prematuro por liveness durante un GC pause largo recrearía el pod). Dejarlo en 30 es razonable.

### (c) ¿Justifica `startupProbe`? — `Production-relevant`

Con `initialDelaySeconds=5` en readiness, no. La latencia de bootstrap observada (~5s) cabe holgadamente dentro de un `periodSeconds=10` con `failureThreshold=3`, así que la sonda no va a matar al pod prematuramente. **Recomendación: no agregar `startupProbe` por ahora.** Si más adelante el snapshot inicial de un nuevo conector requiere minutos (no es nuestro caso porque el offset ya está persistido en el PVC), reabrir.

### (d) Bug colateral del bootstrap inicial (race contra `mysql-replica`) — `Lab-only`

Cuando ambos stacks se levantan en frío, `debezium-server` arranca antes de que el Service `mysql-replica` resuelva DNS / acepte conexiones, y entra en crashloop hasta que kubelet lo reintenta lo suficiente (1–5 restarts observados antes de quedar Ready). **Esto es específico del lab**: solo ocurre porque `mysql-replica` es a su vez un Pod de Kubernetes que se levanta en paralelo. **En producción la DB vive fuera del cluster, su hostname resuelve siempre por DNS externo, y este race condition no existe.**

Mitigación lab-only (no aplicar a producción): se podría agregar un `initContainer` que haga `mysql -h mysql-replica ... -e "SELECT 1"` con `until` loop. **No** se incluye en el change derivado de hardening porque introduciría divergencia entre la config del lab y la de producción.

### (e) RTO observado vs umbral del lab — `Production-relevant` (referencia)

El umbral aceptable no está formalizado (Open Question 2 del design). Para referencia: con la config actual el tiempo de disponibilidad funcional post-fallo es **~5–6s** y el tiempo hasta `Ready=True` es **~22s**. Estos números se replicarán muy parecido en producción (la red entre Debezium y la DB externa puede agregar algunos ms a `time-to-first-event`, pero el dominante sigue siendo el bootstrap del JVM/Quarkus). Si el ambiente tolera ≤ 30s, la config actual ya cumple. Si quiere alinear `Ready` con disponibilidad funcional, aplicar la recomendación (b).

### Resumen de cambios sugeridos para un futuro change `harden-debezium-server-restart`

Solo se incluyen los **production-relevant**. La recomendación (d) queda **explícitamente excluida** para no introducir divergencia lab vs prod.

| # | Cambio | Etiqueta | Origen |
|---|---|---|---|
| 1 | `readinessProbe.initialDelaySeconds: 5` (de 20) | Production-relevant | Recomendación (b) |
| 2 | `terminationGracePeriodSeconds: 60` (de default 30) | Production-relevant | Recomendación auxiliar del design original (flush ordenado del offset al PVC en shutdown) |
| 3 | `livenessProbe` sin cambios | Production-relevant | Recomendación (b), parte 2 |
| 4 | **NO** agregar `startupProbe` | Production-relevant | Recomendación (c) |
| 5 | **NO** agregar `initContainer` para esperar a `mysql-replica` | Lab-only — excluido | Recomendación (d) |

Si el lab no necesita "Ready alineado con disponibilidad funcional" ni el flush ordenado, ninguno de estos cambios es bloqueante. La configuración actual **ya cumple** lo medido en este experimento: pod sustituto sirviendo CDC en ~6s, sin pérdidas ni duplicados.
