#!/usr/bin/env bash
#
# rto_experiment.sh — Automated RTO measurement for debezium-server in both stacks.
#
# Pre-conditions:
#   - minikube running
#   - namespace `cdc-lab-file` con ambos stacks (label stack=mysql57 y stack=mysql8)
#     y el state-store compartido aplicados
#   - debezium-server-{57,8} con probes que emitan Ready=True dentro del warmup (60s)
#
# What it does:
#   1. Verifies kubectl + namespace + Deployments are ready for both stacks.
#   2. (Re)deploys a long-duration load-generator Job per stack so that the sink
#      receives continuous writes during the experiment.
#   3. Calls rto_measure.py 3 times per stack (configurable), discriminating por label.
#   4. Prints a summary table with min / median / max of time_to_ready_seconds
#      and time_to_first_event_seconds per stack.
#
# Usage:
#   minikube/scripts/rto_experiment.sh [<runs_per_stack>]
#
# Exit codes:
#   0 success, 1 pre-condition failed, 2 measurement script failed.

set -euo pipefail

# --- Configurable knobs ------------------------------------------------------

readonly RUNS_PER_STACK="${1:-3}"

readonly NAMESPACE="cdc-lab-file"

# Each stack: "<stack_label>:<load_target>:<load_host>"
#   stack_label: valor de la label `stack` (mysql57 o mysql8) y discriminador en el nombre
#   load_target: arg --target del random_changes.py (mysql5.7 o mysql8)
#   load_host:   hostname del mysql-primary (mysql-primary-57 o mysql-primary-8)
readonly STACKS=(
  "mysql57:mysql5.7:mysql-primary-57"
  "mysql8:mysql8:mysql-primary-8"
)

readonly LOAD_GENERATOR_LABEL_SELECTOR="app=load-generator"
readonly LOAD_GENERATOR_READY_WAIT_SECONDS=30
readonly ROLLOUT_TIMEOUT_SECONDS=120

# --- Paths -------------------------------------------------------------------

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PYTHON_MEASUREMENT_SCRIPT="${SCRIPT_DIR}/rto_measure.py"
readonly LOAD_GENERATOR_TEMPLATE="${SCRIPT_DIR}/loadgen-long.yaml"

# --- Helpers -----------------------------------------------------------------

log()  { printf "[%(%H:%M:%S)T] %s\n" -1 "$*"; }
fail() { printf "[%(%H:%M:%S)T] ERROR: %s\n" -1 "$*" >&2; exit "${2:-1}"; }

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "missing required command: $1"
}

verify_namespace_exists() {
  local namespace="$1"
  kubectl get namespace "$namespace" >/dev/null 2>&1 \
    || fail "namespace not found: $namespace"
}

verify_debezium_deployment_ready() {
  local stack_label="$1"
  local deployment_name="debezium-server-${stack_label#mysql}"
  kubectl rollout status \
    "deployment/${deployment_name}" \
    -n "${NAMESPACE}" \
    --timeout="${ROLLOUT_TIMEOUT_SECONDS}s" >/dev/null \
    || fail "deployment/${deployment_name} not ready in ${NAMESPACE}"
}

deploy_long_load_generator() {
  local stack_label="$1"   # mysql57 / mysql8
  local target_label="$2"  # mysql5.7 / mysql8
  local target_host="$3"   # mysql-primary-57 / mysql-primary-8

  log "  cleaning previous load-generator Job for stack=${stack_label} (if any)"
  kubectl delete job -n "${NAMESPACE}" \
    -l "${LOAD_GENERATOR_LABEL_SELECTOR},stack=${stack_label}" \
    --ignore-not-found --wait >/dev/null 2>&1 || true

  log "  applying long-duration load-generator (stack=${stack_label} target=${target_label})"
  sed \
    -e "s/__NAMESPACE__/${NAMESPACE}/g" \
    -e "s/__TARGET__/${target_label}/g" \
    -e "s/__STACK_LABEL__/${stack_label}/g" \
    -e "s/__TARGET_HOST__/${target_host}/g" \
    "${LOAD_GENERATOR_TEMPLATE}" \
    | kubectl apply -f - >/dev/null

  log "  waiting up to ${LOAD_GENERATOR_READY_WAIT_SECONDS}s for load-generator pod to be Running"
  local elapsed_seconds=0
  local current_phase=""
  while (( elapsed_seconds < LOAD_GENERATOR_READY_WAIT_SECONDS )); do
    current_phase="$(kubectl get pods -n "${NAMESPACE}" \
      -l "${LOAD_GENERATOR_LABEL_SELECTOR},stack=${stack_label}" \
      -o jsonpath='{.items[0].status.phase}' 2>/dev/null || true)"
    [[ "$current_phase" == "Running" ]] && break
    sleep 2
    elapsed_seconds=$((elapsed_seconds + 2))
  done
  [[ "$current_phase" == "Running" ]] \
    || fail "load-generator did not reach Running within ${LOAD_GENERATOR_READY_WAIT_SECONDS}s for stack ${stack_label}"
}

run_measurements_for_stack() {
  local stack_label="$1"   # mysql57 / mysql8
  local csv_output_path="$2"

  log "Running ${RUNS_PER_STACK} measurement runs on stack=${stack_label}"
  python3 "${PYTHON_MEASUREMENT_SCRIPT}" \
    "${NAMESPACE}" \
    "${RUNS_PER_STACK}" \
    "${stack_label}" \
    --pod-label-selector  "app=debezium-server,stack=${stack_label}" \
    --sink-label-selector "app=cdc-sink,stack=${stack_label}" \
    | tee >(grep '^CSV,' >> "$csv_output_path") \
    || fail "rto_measure.py failed for stack ${stack_label}" 2
}

compute_and_print_summary() {
  local csv_output_path="$1"

  log "Summary (min / median / max):"
  python3 - "$csv_output_path" <<'PYTHON_SUMMARY'
import statistics, sys, re

csv_path = sys.argv[1]
stats_by_stack: dict[str, dict[str, list[float]]] = {}

with open(csv_path) as csv_file:
    for raw_line in csv_file:
        if not raw_line.startswith("CSV,"):
            continue
        # CSV,<ns>,<run_label>,<pod_old>,<pod_new>,<t_delete>,<t_ready>,<t_first_event>,<ttr>,<ttfe>
        fields = raw_line.strip().split(",")
        run_label = fields[2]                       # e.g. "mysql57.1"
        stack_label = re.split(r"[.\s]", run_label, maxsplit=1)[0]
        time_to_ready_seconds = float(fields[8])
        time_to_first_event_seconds = float(fields[9])
        bucket = stats_by_stack.setdefault(
            stack_label,
            {"time_to_ready_seconds": [], "time_to_first_event_seconds": []},
        )
        bucket["time_to_ready_seconds"].append(time_to_ready_seconds)
        bucket["time_to_first_event_seconds"].append(time_to_first_event_seconds)

header = f"{'stack':<10} | {'time_to_ready (s)':>26} | {'time_to_first_event (s)':>26}"
print(header)
print("-" * len(header))
for stack_label, metrics in stats_by_stack.items():
    ready_samples = metrics["time_to_ready_seconds"]
    first_event_samples = metrics["time_to_first_event_seconds"]
    ready_summary = (
        f"{min(ready_samples):.2f} / "
        f"{statistics.median(ready_samples):.2f} / "
        f"{max(ready_samples):.2f}"
    )
    first_event_summary = (
        f"{min(first_event_samples):.2f} / "
        f"{statistics.median(first_event_samples):.2f} / "
        f"{max(first_event_samples):.2f}"
    )
    print(f"{stack_label:<10} | {ready_summary:>26} | {first_event_summary:>26}")
PYTHON_SUMMARY
}

# --- Main --------------------------------------------------------------------

main() {
  require_command kubectl
  require_command python3
  [[ -x "${PYTHON_MEASUREMENT_SCRIPT}" ]] \
    || chmod +x "${PYTHON_MEASUREMENT_SCRIPT}" 2>/dev/null || true

  log "Pre-flight: verifying namespace ${NAMESPACE} and Deployments"
  verify_namespace_exists "${NAMESPACE}"
  for stack_spec in "${STACKS[@]}"; do
    local stack_label="${stack_spec%%:*}"
    verify_debezium_deployment_ready "$stack_label"
    log "  ok: stack=${stack_label}"
  done

  local csv_output_path
  csv_output_path="$(mktemp -t rto_results_XXXXXX.csv)"
  log "CSV output: $csv_output_path"

  for stack_spec in "${STACKS[@]}"; do
    local stack_label="${stack_spec%%:*}"
    local rest="${stack_spec#*:}"
    local target_label="${rest%%:*}"
    local target_host="${rest#*:}"
    log "=== Stack ${stack_label} (target=${target_label} host=${target_host}) ==="
    deploy_long_load_generator "$stack_label" "$target_label" "$target_host"
    run_measurements_for_stack "$stack_label" "$csv_output_path"
  done

  echo
  compute_and_print_summary "$csv_output_path"
  echo
  log "Done. Raw CSV at: $csv_output_path"
}

main "$@"
