# shellcheck shell=bash
# Funciones comunes para los scripts monitor-mysqlX.sh.
# Se espera que el script invocador defina:
#   CONTAINER     — nombre del contenedor de la réplica MySQL
#   MYSQL_PORT    — puerto host del servicio mysql-replica
#   STACK_LABEL   — etiqueta corta para la columna `stack` (e.g., mysql5.7)

set -euo pipefail

INTERVAL=5
DURATION=0          # 0 = corre hasta SIGINT
CSV_MODE=0
HEADER_EVERY=20

usage() {
  cat <<EOF
Uso: $(basename "$0") [-i SECONDS] [-d SECONDS] [--csv] [-h]

  -i N        Intervalo entre muestras en segundos (default: $INTERVAL)
  -d N        Duración total. Si se omite, corre hasta Ctrl+C.
  --csv       Salida CSV (header una sola vez, valores en bytes/seg).
  -h          Esta ayuda.

Ejemplos:
  $(basename "$0") -i 5 -d 60 --csv > captura.csv
  $(basename "$0") | tee /tmp/lectura.log
EOF
}

parse_args() {
  while (( $# > 0 )); do
    case "$1" in
      -i) INTERVAL="$2"; shift 2 ;;
      -d) DURATION="$2"; shift 2 ;;
      --csv) CSV_MODE=1; shift ;;
      -h|--help) usage; exit 0 ;;
      *) echo "Argumento desconocido: $1" >&2; usage; exit 64 ;;
    esac
  done
}

check_container() {
  local running
  running=$(docker inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null || true)
  if [[ -z "$running" ]]; then
    echo "Error: contenedor '$CONTAINER' no encontrado. ¿El stack está arriba?" >&2
    exit 2
  fi
  if [[ "$running" != "true" ]]; then
    echo "Error: contenedor '$CONTAINER' existe pero está detenido. Arráncalo con 'docker compose up -d'." >&2
    exit 2
  fi
}

# Convierte string tipo "7.89MB" / "1.23kB" / "256.4MiB" / "0B" a bytes (entero).
to_bytes() {
  awk -v s="$1" 'BEGIN {
    n = s + 0
    u = s; sub(/^[0-9.]+/, "", u); u = tolower(u)
    if (u == "" || u == "b") m = 1
    else if (u ~ /^k/) m = 1024
    else if (u ~ /^m/) m = 1024 * 1024
    else if (u ~ /^g/) m = 1024 * 1024 * 1024
    else if (u ~ /^t/) m = 1024 * 1024 * 1024 * 1024
    else m = 0
    printf "%.0f", n * m
  }'
}

# Formatea bytes a humano (K/M/G).
fmt_bytes() {
  awk -v b="$1" 'BEGIN {
    if (b < 1024) printf "%dB", b
    else if (b < 1024*1024) printf "%.1fK", b/1024
    else if (b < 1024*1024*1024) printf "%.1fM", b/(1024*1024)
    else printf "%.1fG", b/(1024*1024*1024)
  }'
}

# Muestra los counters cumulativos del contenedor a stdout en formato:
# CPU_PCT MEM_BYTES BLK_R BLK_W NET_RX NET_TX
read_docker_stats() {
  local raw cpu mem net blk
  raw=$(docker stats --no-stream --format '{{.CPUPerc}}|{{.MemUsage}}|{{.NetIO}}|{{.BlockIO}}' "$CONTAINER" 2>/dev/null) || {
    echo "ERR ERR ERR ERR ERR ERR"
    return 0
  }
  cpu="${raw%%|*}"; raw="${raw#*|}"
  mem="${raw%%|*}"; raw="${raw#*|}"
  net="${raw%%|*}"; raw="${raw#*|}"
  blk="$raw"

  cpu="${cpu%\%}"
  local mem_used="${mem%% *}"
  local net_rx net_tx blk_r blk_w
  net_rx="${net%% / *}"; net_tx="${net##* / }"
  blk_r="${blk%% / *}"; blk_w="${blk##* / }"

  printf '%s %s %s %s %s %s\n' \
    "$cpu" \
    "$(to_bytes "$mem_used")" \
    "$(to_bytes "$blk_r")" \
    "$(to_bytes "$blk_w")" \
    "$(to_bytes "$net_rx")" \
    "$(to_bytes "$net_tx")"
}

# Imprime los counters de SHOW GLOBAL STATUS, uno por línea: NAME VALUE.
# Si MySQL falla, imprime "ERR" para cada counter solicitado.
# Usamos `docker exec` para no depender del cliente mysql en el host.
read_mysql_status() {
  local out
  out=$(docker exec -i "$CONTAINER" mysql -uroot -proot -N -B -e "
    SHOW GLOBAL STATUS WHERE Variable_name IN (
      'Innodb_data_read','Innodb_data_written',
      'Bytes_sent','Bytes_received',
      'Binlog_cache_use','Binlog_cache_disk_use'
    )" 2>/dev/null) || {
    printf '%s ERR\n' Innodb_data_read Innodb_data_written Bytes_sent Bytes_received Binlog_cache_use Binlog_cache_disk_use
    return 0
  }
  printf '%s\n' "$out"
}

# Construye un asociativo (en realidad expande variables) a partir de la salida
# tab-separated de read_mysql_status.
mysql_value() {
  local name="$1"
  awk -v n="$name" '$1 == n { print $2; found=1 } END { if (!found) print "ERR" }' <<<"$2"
}

# Calcula (current - prev) / interval. Si alguno es ERR, devuelve "?".
delta_rate() {
  local cur="$1" prev="$2" interval="$3"
  if [[ "$cur" == "ERR" || "$prev" == "ERR" || "$cur" == "?" || "$prev" == "?" ]]; then
    echo "?"
    return
  fi
  awk -v c="$cur" -v p="$prev" -v i="$interval" 'BEGIN {
    if (i <= 0) { print "?"; exit }
    d = (c - p) / i
    if (d < 0) d = 0
    printf "%.0f", d
  }'
}

print_csv_header() {
  echo "timestamp,stack,cpu_pct,mem_bytes,blkio_read_bps,blkio_write_bps,netio_rx_bps,netio_tx_bps,innodb_read_bps,innodb_write_bps,mysql_bytes_sent_bps,mysql_bytes_recv_bps,binlog_cache_use_delta,binlog_cache_disk_use_delta"
}

print_human_header() {
  printf '%-19s %-9s %5s %9s %9s %9s %9s %9s %9s %9s %9s %5s\n' \
    'timestamp' 'stack' 'cpu%' 'mem' 'blk_r/s' 'blk_w/s' 'net_tx/s' 'innodb_r/s' 'innodb_w/s' 'mysql_tx/s' 'mysql_rx/s' 'bnlc'
}

print_csv_row() {
  # args: ts stack cpu mem blk_r blk_w net_rx net_tx idb_r idb_w bs br bnlc bnlcd
  printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' "$@"
}

print_human_row() {
  local ts="$1" stack="$2" cpu="$3" mem="$4" blk_r="$5" blk_w="$6" net_tx="$7" idb_r="$8" idb_w="$9" bs="${10}" br="${11}" bnlc="${12}"
  fmt_or_q() { [[ "$1" == "?" || "$1" == "baseline" ]] && echo "$1" || fmt_bytes "$1"; }
  printf '%-19s %-9s %5s %9s %9s %9s %9s %9s %9s %9s %9s %5s\n' \
    "$ts" "$stack" "${cpu}" \
    "$(fmt_or_q "$mem")" \
    "$(fmt_or_q "$blk_r")" "$(fmt_or_q "$blk_w")" \
    "$(fmt_or_q "$net_tx")" \
    "$(fmt_or_q "$idb_r")" "$(fmt_or_q "$idb_w")" \
    "$(fmt_or_q "$bs")" "$(fmt_or_q "$br")" \
    "$bnlc"
}

declare -i STOP=0
on_signal() {
  STOP=1
}

run_monitor() {
  parse_args "$@"
  check_container
  trap on_signal SIGINT SIGTERM

  # Línea de progreso a stderr para que el usuario vea actividad inmediata.
  echo "[monitor] $STACK_LABEL: capturando cada ${INTERVAL}s${DURATION:+ durante ${DURATION}s}. Ctrl+C para parar." >&2

  if (( CSV_MODE )); then
    print_csv_header
  else
    print_human_header
  fi

  # Imprimir la fila baseline INMEDIATAMENTE (antes de la primera llamada lenta a
  # docker stats / mysql), para que aparezca en el archivo aunque el usuario
  # mate el script muy pronto.
  local ts0; ts0=$(date -Iseconds)
  if (( CSV_MODE )); then
    print_csv_row "$ts0" "$STACK_LABEL" baseline baseline baseline baseline baseline baseline baseline baseline baseline baseline baseline baseline
  else
    print_human_row "$ts0" "$STACK_LABEL" baseline baseline baseline baseline baseline baseline baseline baseline baseline baseline
  fi

  local started_at; started_at=$(date +%s)
  local iter=0
  local prev_blk_r=ERR prev_blk_w=ERR prev_net_rx=ERR prev_net_tx=ERR
  local prev_idb_r=ERR prev_idb_w=ERR prev_bs=ERR prev_br=ERR prev_bnlc=ERR prev_bnlcd=ERR

  while (( STOP == 0 )); do
    if (( DURATION > 0 )) && (( $(date +%s) - started_at >= DURATION )); then
      break
    fi

    local ts; ts=$(date -Iseconds)
    read -r cpu mem blk_r blk_w net_rx net_tx <<<"$(read_docker_stats)"
    local mysql_out; mysql_out=$(read_mysql_status)
    local idb_r idb_w bs br bnlc bnlcd
    idb_r=$(mysql_value Innodb_data_read   "$mysql_out")
    idb_w=$(mysql_value Innodb_data_written "$mysql_out")
    bs=$(mysql_value Bytes_sent             "$mysql_out")
    br=$(mysql_value Bytes_received         "$mysql_out")
    bnlc=$(mysql_value Binlog_cache_use     "$mysql_out")
    bnlcd=$(mysql_value Binlog_cache_disk_use "$mysql_out")

    if (( iter == 0 )); then
      # iter 0 solo guarda los counters como prev_* para calcular deltas en iter >= 1.
      # El baseline ya se imprimió antes del loop.
      :
    else
      local r_blk_r r_blk_w r_net_rx r_net_tx r_idb_r r_idb_w r_bs r_br r_bnlc r_bnlcd
      r_blk_r=$(delta_rate "$blk_r" "$prev_blk_r" "$INTERVAL")
      r_blk_w=$(delta_rate "$blk_w" "$prev_blk_w" "$INTERVAL")
      r_net_rx=$(delta_rate "$net_rx" "$prev_net_rx" "$INTERVAL")
      r_net_tx=$(delta_rate "$net_tx" "$prev_net_tx" "$INTERVAL")
      r_idb_r=$(delta_rate "$idb_r" "$prev_idb_r" "$INTERVAL")
      r_idb_w=$(delta_rate "$idb_w" "$prev_idb_w" "$INTERVAL")
      r_bs=$(delta_rate "$bs" "$prev_bs" "$INTERVAL")
      r_br=$(delta_rate "$br" "$prev_br" "$INTERVAL")
      r_bnlc=$(delta_rate "$bnlc" "$prev_bnlc" 1)
      r_bnlcd=$(delta_rate "$bnlcd" "$prev_bnlcd" 1)

      if (( CSV_MODE )); then
        print_csv_row "$ts" "$STACK_LABEL" "${cpu:-?}" "${mem:-?}" "$r_blk_r" "$r_blk_w" "$r_net_rx" "$r_net_tx" "$r_idb_r" "$r_idb_w" "$r_bs" "$r_br" "$r_bnlc" "$r_bnlcd"
      else
        # print_human_row firma: ts stack cpu mem blk_r blk_w net_tx idb_r idb_w bs br bnlc (12 args; net_rx no se imprime en humano)
        print_human_row "$ts" "$STACK_LABEL" "${cpu:-?}" "$mem" "$r_blk_r" "$r_blk_w" "$r_net_tx" "$r_idb_r" "$r_idb_w" "$r_bs" "$r_br" "$r_bnlc"
        if (( iter % HEADER_EVERY == 0 )); then
          print_human_header
        fi
      fi
    fi

    prev_blk_r=$blk_r prev_blk_w=$blk_w prev_net_rx=$net_rx prev_net_tx=$net_tx
    prev_idb_r=$idb_r prev_idb_w=$idb_w prev_bs=$bs prev_br=$br
    prev_bnlc=$bnlc prev_bnlcd=$bnlcd
    iter=$((iter + 1))

    # Sleep tolerante a señales.
    sleep "$INTERVAL" &
    wait $! 2>/dev/null || true
  done

  if (( CSV_MODE == 0 )); then
    echo "# stopped after $iter iterations" >&2
  fi
}
