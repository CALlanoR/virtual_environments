#!/usr/bin/env bash
set -uo pipefail

CONNECT_URL="${CONNECT_URL:-http://localhost:8083}"

# ── Colores ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC}    $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*"; }

color_state() {
  case "$1" in
    RUNNING) echo -e "${GREEN}$1${NC}" ;;
    FAILED)  echo -e "${RED}$1${NC}" ;;
    *)       echo -e "${YELLOW}$1${NC}" ;;
  esac
}

# ── Helpers ────────────────────────────────────────────────────────────────────
wait_for_connect() {
  echo "Esperando que Kafka Connect esté listo..."
  until curl -sf "${CONNECT_URL}/" > /dev/null; do
    sleep 2
  done
  ok "Kafka Connect listo en ${CONNECT_URL}"
}

register() {
  local name="$1"
  local file="$2"

  echo ""
  echo "Registrando: ${name}"

  local response http_code body
  response=$(curl -s -w "\n%{http_code}" -X POST "${CONNECT_URL}/connectors" \
    -H "Content-Type: application/json" \
    -d @"${file}")

  http_code=$(echo "$response" | tail -1)
  body=$(echo "$response" | head -n -1)

  case "$http_code" in
    201) ok "Conector '${name}' creado correctamente." ;;
    409) warn "Conector '${name}' ya existe, omitiendo registro." ;;
    *)
      err "Fallo al registrar '${name}' (HTTP ${http_code}):"
      echo "$body" | jq -r '.message // .' 2>/dev/null || echo "$body"
      ;;
  esac
}

check_status() {
  local name="$1"

  local http_code status
  status=$(curl -s -w "\n%{http_code}" "${CONNECT_URL}/connectors/${name}/status")
  http_code=$(echo "$status" | tail -1)
  status=$(echo "$status" | head -n -1)

  if [[ "$http_code" == "404" ]]; then
    echo ""
    err "Conector '${name}' no encontrado."
    return
  fi

  local connector_state task_count
  connector_state=$(echo "$status" | jq -r '.connector.state // "UNKNOWN"')
  task_count=$(echo "$status" | jq '.tasks | length')

  echo ""
  echo "  Conector : ${name}"
  echo "  Estado   : $(color_state "$connector_state")"

  if [[ "$task_count" -eq 0 ]]; then
    warn "  Sin tareas asignadas aún."
    return
  fi

  local i=0
  while [[ $i -lt $task_count ]]; do
    local task_state trace
    task_state=$(echo "$status" | jq -r ".tasks[$i].state")
    trace=$(echo "$status"     | jq -r ".tasks[$i].trace // empty")

    echo "  Task[$i]  : $(color_state "$task_state")"

    if [[ -n "$trace" ]]; then
      err "  Traza de error:"
      echo "$trace" | grep -E "^(Caused by|.*Exception|.*Error)" | head -5 \
        | sed 's/^/    /'
    fi
    ((i++))
  done
}

print_status_all() {
  echo ""
  echo -e "${CYAN}════════════════════════════════════════${NC}"
  echo -e "${CYAN} Estado de los conectores${NC}"
  echo -e "${CYAN}════════════════════════════════════════${NC}"
  check_status "mysql-source-connector"
  check_status "s3-sink-bronze"
  echo ""
}

# ── Uso ───────────────────────────────────────────────────────────────────────
usage() {
  echo ""
  echo "Uso: $0 <comando>"
  echo ""
  echo "Comandos:"
  echo "  register   Registra los conectores MySQL source y S3 sink"
  echo "  status     Muestra el estado de todos los conectores"
  echo ""
  echo "Variables de entorno:"
  echo "  CONNECT_URL  URL de Kafka Connect (default: http://localhost:8083)"
  echo ""
}

# ── Main ──────────────────────────────────────────────────────────────────────
case "${1:-}" in
  register)
    wait_for_connect
    register "mysql-source-connector" "connector-mysql-source.json"
    register "s3-sink-bronze"         "connector-s3-sink.json"
    print_status_all
    ;;
  status)
    wait_for_connect
    print_status_all
    ;;
  *)
    err "Comando inválido: '${1:-}'"
    usage
    exit 1
    ;;
esac
