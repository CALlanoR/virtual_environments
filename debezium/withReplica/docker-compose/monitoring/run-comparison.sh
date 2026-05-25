#!/usr/bin/env bash
# run-comparison.sh
#
# Orquestador de captura comparativa I/O entre los stacks mysql5.7 y mysql8.
#
# Flujo (~80s por defecto):
#   t=0    arrancan ambos monitores
#   t=20   arrancan ambos random_changes.py
#   t=60   los generadores auto-terminan
#   t=80   los monitores auto-terminan
#   t=80+  se genera el PNG comparativo
#
# Pre-requisitos:
#   - Ambos stacks corriendo (`make up && make wait-healthy`)
#   - Venv del load-generator: `cd load-generator && make venv`
#   - Venv del plot:           `cd monitoring/plot && make venv`
#
# Overrides vía variables de entorno (todos opcionales):
#   PRELOAD_S        baseline antes de la carga (default 20)
#   LOAD_S           duración de la carga (default 40)
#   POSTLOAD_S       cooldown después de la carga (default 20)
#   INTERVAL_MONITOR intervalo del monitor en segundos (default 1)
#   CSV57            ruta del CSV de mysql5.7 (default /tmp/mysql57.csv)
#   CSV8             ruta del CSV de mysql8 (default /tmp/mysql8.csv)
#   OUT              ruta del PNG (default /tmp/comparison.png)

set -euo pipefail

# ----- ubicaciones -----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WITHREPLICA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LG_PY="$WITHREPLICA_DIR/load-generator/.venv/bin/python"
LG_SCRIPT="$WITHREPLICA_DIR/load-generator/random_changes.py"
PLOT_PY="$SCRIPT_DIR/plot/.venv/bin/python"
PLOT_SCRIPT="$SCRIPT_DIR/plot/plot.py"

# ----- defaults overrideables vía env -----
PRELOAD_S="${PRELOAD_S:-20}"
LOAD_S="${LOAD_S:-40}"
POSTLOAD_S="${POSTLOAD_S:-20}"
INTERVAL_MONITOR="${INTERVAL_MONITOR:-1}"
CSV57="${CSV57:-/tmp/mysql57.csv}"
CSV8="${CSV8:-/tmp/mysql8.csv}"
OUT="${OUT:-/tmp/comparison.png}"

usage() {
  cat <<EOF
Uso: $(basename "$0") [-h|--help]

Captura I/O de los dos stacks bajo carga sintética y genera un PNG comparativo.
Los parámetros se pasan vía variables de entorno (todas opcionales):

  PRELOAD_S=$PRELOAD_S         baseline antes de la carga
  LOAD_S=$LOAD_S            duración de la carga
  POSTLOAD_S=$POSTLOAD_S        cooldown después de la carga
  INTERVAL_MONITOR=$INTERVAL_MONITOR   intervalo del monitor (segundos)
  CSV57=$CSV57   path del CSV de mysql5.7
  CSV8=$CSV8     path del CSV de mysql8
  OUT=$OUT     path del PNG resultante

Ejemplo con run corto:
  LOAD_S=10 PRELOAD_S=5 POSTLOAD_S=5 $(basename "$0")

Pre-requisitos: ambos stacks healthy + venvs creados (load-generator y plot).
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "") ;;
  *) echo "Argumento desconocido: $1" >&2; usage; exit 64 ;;
esac

# ----- pre-flight -----
fail() { echo "Error: $*" >&2; exit 2; }

check_running() {
  local container="$1"
  local running
  running=$(docker inspect -f '{{.State.Running}}' "$container" 2>/dev/null || true)
  if [[ -z "$running" ]]; then
    fail "contenedor '$container' no encontrado. ¿Ejecutaste 'make up'?"
  fi
  if [[ "$running" != "true" ]]; then
    fail "contenedor '$container' existe pero está detenido. Ejecuta 'make up'."
  fi
}

echo "[run-comparison] pre-flight..."
check_running "mysql-replica"
check_running "mysql8-replica"

[[ -x "$LG_PY" ]]   || fail "venv del load-generator no encontrado en $LG_PY. Corre: cd $WITHREPLICA_DIR/load-generator && make venv"
[[ -f "$LG_SCRIPT" ]] || fail "$LG_SCRIPT no existe"
[[ -x "$PLOT_PY" ]] || fail "venv del plot no encontrado en $PLOT_PY. Corre: cd $SCRIPT_DIR/plot && make venv"
[[ -f "$PLOT_SCRIPT" ]] || fail "$PLOT_SCRIPT no existe"

TOTAL_S=$((PRELOAD_S + LOAD_S + POSTLOAD_S))

echo "[run-comparison] config:"
echo "  PRELOAD_S=$PRELOAD_S  LOAD_S=$LOAD_S  POSTLOAD_S=$POSTLOAD_S  TOTAL=${TOTAL_S}s"
echo "  INTERVAL_MONITOR=$INTERVAL_MONITOR"
echo "  CSV57=$CSV57"
echo "  CSV8=$CSV8"
echo "  OUT=$OUT"
echo ""

# ----- limpieza ante señal -----
declare -a CHILDREN=()
INTERRUPTED=0
on_signal() {
  INTERRUPTED=1
  echo "" >&2
  echo "[run-comparison] señal recibida — terminando hijos..." >&2
  for pid in "${CHILDREN[@]}"; do
    kill -TERM "$pid" 2>/dev/null || true
  done
  # dejar que terminen un instante; luego forzar
  sleep 1
  for pid in "${CHILDREN[@]}"; do
    kill -KILL "$pid" 2>/dev/null || true
  done
  echo "[run-comparison] interrumpido. CSVs parciales en $CSV57 y $CSV8 (sin plot)." >&2
  exit 130
}
trap on_signal SIGINT SIGTERM

# ----- fase 1: lanzar monitores (-d $TOTAL_S) -----
echo "[t=0] arrancando monitores (durarán ${TOTAL_S}s)..."
"$SCRIPT_DIR/monitor-mysql5.7.sh" --csv -i "$INTERVAL_MONITOR" -d "$TOTAL_S" > "$CSV57" 2>/dev/null &
M57_PID=$!; CHILDREN+=("$M57_PID")
"$SCRIPT_DIR/monitor-mysql8.sh"   --csv -i "$INTERVAL_MONITOR" -d "$TOTAL_S" > "$CSV8" 2>/dev/null &
M8_PID=$!;  CHILDREN+=("$M8_PID")

# ----- fase 2: baseline pre-load -----
echo "[t=0] capturando baseline durante ${PRELOAD_S}s..."
sleep "$PRELOAD_S"

# ----- fase 3: lanzar generadores -----
echo "[t=${PRELOAD_S}] arrancando random_changes.py para ambos stacks (cada 1s, ${LOAD_S}s)..."
"$LG_PY" "$LG_SCRIPT" --target mysql5.7 -i 1 -d "$LOAD_S" >/tmp/run-comparison-lg57.log 2>&1 &
LG57_PID=$!; CHILDREN+=("$LG57_PID")
"$LG_PY" "$LG_SCRIPT" --target mysql8   -i 1 -d "$LOAD_S" >/tmp/run-comparison-lg8.log 2>&1 &
LG8_PID=$!;  CHILDREN+=("$LG8_PID")

# ----- fase 4: esperar generadores -----
wait "$LG57_PID" || echo "[warn] random_changes.py mysql5.7 exit=$?"
wait "$LG8_PID"  || echo "[warn] random_changes.py mysql8 exit=$?"
echo "[t=$((PRELOAD_S + LOAD_S))] ambos generadores terminaron. Ops registradas:"
echo "  mysql5.7: $(grep -cE 'INSERT|UPDATE|DELETE' /tmp/run-comparison-lg57.log || echo 0)"
echo "  mysql8:   $(grep -cE 'INSERT|UPDATE|DELETE' /tmp/run-comparison-lg8.log  || echo 0)"

# ----- fase 5: cooldown (los monitores siguen capturando solos) -----
echo "[t=$((PRELOAD_S + LOAD_S))] cooldown ${POSTLOAD_S}s..."
wait "$M57_PID" || echo "[warn] monitor-mysql5.7 exit=$?"
wait "$M8_PID"  || echo "[warn] monitor-mysql8 exit=$?"

# ----- fase 6: plot -----
echo "[t=${TOTAL_S}+] generando PNG..."
"$PLOT_PY" "$PLOT_SCRIPT" "$CSV57" "$CSV8" -o "$OUT" \
  --title "Comparación I/O — mysql5.7 vs mysql8 (${TOTAL_S}s)"

echo ""
echo "[run-comparison] ✓ done"
echo "  CSV mysql5.7: $CSV57 ($(wc -l < "$CSV57") líneas)"
echo "  CSV mysql8:   $CSV8  ($(wc -l < "$CSV8") líneas)"
echo "  Plot:         $OUT"
