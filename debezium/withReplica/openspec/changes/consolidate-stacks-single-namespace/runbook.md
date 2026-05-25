# Runbook — Consolidate stacks to a single namespace `cdc-lab`

Bitácora paso a paso del cutover. Ejecutado el `2026-05-14`. Reproducible desde cero por otra persona sin contexto previo.

## 1. Estado de partida

Lab post `migrate-debezium-state-to-mysql` (archivado): dos namespaces `cdc-mysql57` y `cdc-mysql8`, cada uno con su `mysql-debezium-state` per-stack. `kubectl get all -A | grep cdc-` confirma 9 recursos por namespace antes del cutover (snapshots guardados en `/tmp/snapshot-57-pre.txt` y `/tmp/snapshot-8-pre.txt` para referencia).

## 2. Decisiones operativas

- **Namespace nuevo:** `cdc-lab`.
- **Sufijo:** `-57` / `-8` para todos los recursos que existían duplicados.
- **Labels:** `stack: mysql57` / `mysql8` en todos los recursos para selectores.
- **State-store único:** `mysql-debezium-state` (sin sufijo) con DBs `dbz_state_57` y `dbz_state_8`, dos usuarios separados.
- **Greenfield:** no se migra offset viejo; Debezium re-snapshotea al levantar.

## 3. Inventario de cambios aplicados

Total de archivos tocados: **22**.

### Creados (3)

- `minikube/shared/00-namespace.yaml`
- `minikube/shared/04a-mysql-debezium-state.yaml`
- (este runbook)

### Renombrados + reescritos (12)

`minikube/mysql{5.7,8}/01-configmaps{.yaml → -{57,8}.yaml}` y `02-secrets`, `03-mysql-primary`, `04-mysql-replica`, `05-cdc-sink`, `06-debezium-server`. Cambios estándar en cada uno:

- `namespace: cdc-mysql{57,8}` → `namespace: cdc-lab`
- Cada `metadata.name` de StatefulSet, Deployment, Service, ConfigMap y Secret recibe sufijo `-57` o `-8`.
- Todas las referencias internas (selectores, volumeClaimTemplates serviceName, env hostnames, configMap mounts, secret refs) actualizadas al nuevo nombre.
- Label `stack: mysql{57|8}` agregada a `metadata.labels`, `spec.selector.matchLabels` y `spec.template.metadata.labels` de los workloads.
- En `06-debezium-server-*.yaml`: `secretKeyRef.key` pasa de `dbz-state-password` a `dbz-state-{57|8}-password` (Secret único).
- En `01-configmaps-*.yaml` (entry `debezium-config-*`): la JDBC URL pasa de `mysql-debezium-state:3306/dbz_state` a `dbz_state_{57|8}`, y el `jdbc.user` pasa a `dbz_state_{57|8}`.

### Eliminados (4)

- `minikube/mysql5.7/00-namespace.yaml`, `minikube/mysql5.7/04a-mysql-debezium-state.yaml`
- `minikube/mysql8/00-namespace.yaml`, `minikube/mysql8/04a-mysql-debezium-state.yaml`

### Scripts modificados (2)

- `minikube/Makefile` — variables `NS57`/`NS8` consolidadas a `NS=cdc-lab`. Targets `up`/`down`/`ps`/`wait-healthy-*`/`logs-sink-*`/`load-*` reescritos para selectores por label en lugar de namespace.
- `minikube/scripts/loadgen-long.yaml` — nuevos placeholders `__STACK_LABEL__` y `__TARGET_HOST__` (para que el load-generator se pueda invocar contra cualquiera de los dos stacks por label).

### Kustomize modificado (2)

- `minikube/load-generator/mysql5.7/kustomization.yaml` y `.../mysql8/kustomization.yaml` — `namespace: cdc-lab` (ambos generan la misma ConfigMap idempotente).

## 4. Pasos del cutover

### 4.1 Pre-condiciones (Tasks 1.x)

```bash
ls openspec/changes/archive/ | grep migrate         # confirma migrate-* archivado
kubectl get all,pvc,cm,secrets -n cdc-mysql57 > /tmp/snapshot-57-pre.txt
kubectl get all,pvc,cm,secrets -n cdc-mysql8  > /tmp/snapshot-8-pre.txt
kubectl describe node minikube | grep -E "cpu|memory"   # 16 cores / 23GB → margen sobrado
```

### 4.2 Crear shared/ (Tasks 2.x)

```bash
kubectl apply -f minikube/shared/                    # namespace + state-store
kubectl rollout status deployment/mysql-debezium-state -n cdc-lab --timeout=180s
```

Verificación de DBs y usuarios:

```bash
ROOT=$(kubectl get secret -n cdc-lab debezium-state-credentials -o jsonpath='{.data.root-password}' | base64 -d)
kubectl exec -n cdc-lab deploy/mysql-debezium-state -- mysql -uroot -p"$ROOT" -e \
  "SHOW DATABASES; SELECT user, plugin FROM mysql.user WHERE user LIKE 'dbz_state%';"
```

→ confirma `dbz_state_57` y `dbz_state_8` (DBs y usuarios), ambos `mysql_native_password`.

### 4.3 Renombrar/reescribir manifests (Tasks 3.x + 4.x + 5.x + 6.x + 7.x)

Pasos mecánicos (ver sección 3). Lo único no-trivial fue:
- **NodePort collision al aplicar:** los namespaces viejos seguían reservando 30306/30307/30308/30309. Cambié los nuevos a 30406/30407/30408/30409 para coexistir durante la transición. **Si se aplica el cutover desde cero (sin lab previo), los NodePorts originales se pueden conservar** — los puertos 30406-30409 son una decisión circunstancial, no de diseño.

### 4.4 Aplicar stacks (Tasks 8.x)

```bash
kubectl apply -f minikube/mysql5.7/
kubectl apply -k minikube/load-generator/mysql5.7/
kubectl apply -f minikube/mysql8/
kubectl apply -k minikube/load-generator/mysql8/
```

Race condition esperado en cold start (mismo que documentamos en `evaluate-debezium-server-ha`): `debezium-server-{57,8}` reinicia 3–4 veces antes de quedar Ready porque arranca antes de que `mysql-replica-{57,8}` resuelva DNS. **Lab-only**, no requiere intervención — kubelet retry suficiente.

Confirmación post-arranque (~2 min):

```bash
kubectl get pods -n cdc-lab    # 9 pods, todos Ready=1/1
```

Verificación de aislamiento entre stacks:

```bash
PW57=$(kubectl get secret -n cdc-lab debezium-state-credentials -o jsonpath='{.data.dbz-state-57-password}' | base64 -d)
kubectl exec -n cdc-lab deploy/mysql-debezium-state -- mysql -u dbz_state_57 -p"$PW57" -e \
  "SELECT * FROM dbz_state_8.offset_storage LIMIT 1;"
# → ERROR 1142 (42000): SELECT command denied  ✓ aislamiento confirmado
```

### 4.5 No-duplicación

Verificación: ningún `(file, pos)` (mysql57) ni `gtid` (mysql8) aparece dos veces en los logs del sink tras los restarts del cold-start. Debezium reanudó limpiamente desde `dbz_state_{57,8}.offset_storage`.

```bash
kubectl logs -n cdc-lab deploy/cdc-sink-57 --tail=2000 \
  | grep -oE '"file": *"[^"]*",[[:space:]]*"pos": *[0-9]+' | sort | uniq -c | awk '$1 > 1'
kubectl logs -n cdc-lab deploy/cdc-sink-8 --tail=2000 \
  | grep -oE '"gtid": *"[^"]*"' | sort | uniq -c | awk '$1 > 1'
# Salida vacía en ambos → cero duplicados.
```

### 4.6 Cutover destructivo (Tasks 10.x)

```bash
kubectl delete namespace cdc-mysql57 --wait=true
kubectl delete namespace cdc-mysql8  --wait=true
kubectl get ns | grep cdc-               # → solo cdc-lab Active
```

Confirmado: el sink de `cdc-lab` sigue recibiendo eventos del load-generator post-cutover.

## 5. Tropiezos durante la implementación

### 5.1 NodePort collision durante la transición

Síntoma: `Service "mysql-primary-nodeport-57" is invalid: spec.ports[0].nodePort: Invalid value: 30306: provided port is already allocated`.

Causa: `cdc-mysql57` aún existía y tenía un Service NodePort en 30306. NodePorts son cluster-wide, no namespace-scoped.

Fix circunstancial (aplicado): cambiar los nuevos NodePorts a 30406-30409. Una vez completado el cutover (namespaces viejos borrados), los puertos originales quedan libres y se podría revertir a 30306-30309 con un `sed`. **No lo revertí** — los nuevos puertos están documentados y funcionan; cambiarlos otra vez es churn sin beneficio.

## 6. Discrepancias respecto al design

### 6.1 Decisión 6 — orden de migración no se siguió al pie de la letra

El design dijo "crear cdc-lab, validar, **solo entonces** borrar los namespaces viejos". En la práctica, el cutover destructivo ocurrió **después** de validar funcionalidad (snapshot completo, sink recibiendo, aislamiento, no-duplicación), tal como dice el design — pero **con los namespaces viejos coexistiendo** durante todo el periodo de validación (~10 min). Eso obligó al cambio de NodePort (5.1). No hay impacto funcional; solo un par de puertos diferentes.

### 6.2 Sin nada más relevante

El resto del design (sufijos, labels, state-store único con dos DBs, dos usuarios sin grants cruzados, scripts adaptados a label-selectors) se cumplió exactamente como estaba escrito.

## 7. Rollback

Si en algún momento hay que volver a la topología de dos namespaces:

1. Re-aplicar los manifests antiguos (versionados en el commit anterior a este change): `kubectl apply -f minikube_pre/mysql5.7/` y `mysql8/`. Eso recrea `cdc-mysql57` y `cdc-mysql8` con todos sus recursos.
2. Borrar `cdc-lab` por entero: `kubectl delete namespace cdc-lab`.
3. Recrear el state-store en cada namespace según `migrate-debezium-state-to-mysql`. Debezium re-snapshoteará (es greenfield porque el state-store nuevo está vacío).

**Costo del rollback:** ~2 min de indisponibilidad por stack + un re-snapshot visible al sink.

## 8. Anexo — Comandos útiles del nuevo lab

```bash
# Ver todo el lab
kubectl get all -n cdc-lab

# Ver solo un stack
kubectl get pods -n cdc-lab -l stack=mysql57
kubectl get pods -n cdc-lab -l stack=mysql8

# Logs del Debezium de un stack específico
kubectl logs -n cdc-lab -l app=debezium-server,stack=mysql57 -f

# Borrar solo un stack (preserva state-store y el otro stack)
kubectl delete all,configmaps,secrets,pvc -n cdc-lab -l stack=mysql57

# Borrar todo el lab
make -C minikube down
```
