#!/usr/bin/env python3
"""
RTO measurement for debezium-server in a single namespace.

Kills the active debezium-server pod with `kubectl delete --grace-period=0 --force`
and measures two metrics per run:

  - time_to_ready_seconds:       wall time between delete and Ready=True on the
                                 replacement pod (Kubernetes recovery latency).
  - time_to_first_event_seconds: wall time between delete and the first POST
                                 received at the cdc-sink whose source IP matches
                                 the replacement pod (functional latency).

Filtering sink events by source IP is required to discard in-flight POSTs from
the previous pod that arrive at the sink milliseconds after the delete and would
otherwise be misattributed to the replacement pod.

Usage:
  rto_measure.py <namespace> [<num_runs>] [<run_label_prefix>]
                 [--pod-label-selector <selector>]
                 [--sink-label-selector <selector>]

Defaults:
  --pod-label-selector  app=debezium-server
  --sink-label-selector app=cdc-sink

Post-consolidación (consolidate-stacks-single-namespace), invocar con selectores
explícitos para discriminar stack:
  rto_measure.py cdc-lab-file 3 mysql8 \\
      --pod-label-selector  app=debezium-server,stack=mysql8 \\
      --sink-label-selector app=cdc-sink,stack=mysql8

Outputs one CSV line per run with prefix "CSV," for easy parsing by callers.
"""
from __future__ import annotations

import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone


WARMUP_REQUIRED_SECONDS = 60
READY_POLL_INTERVAL_SECONDS = 0.1
READY_POLL_TIMEOUT_SECONDS = 180
FIRST_EVENT_POLL_INTERVAL_SECONDS = 0.2
FIRST_EVENT_POLL_TIMEOUT_SECONDS = 120
SINK_TAIL_ATTACH_SETTLE_SECONDS = 1

DEFAULT_DEBEZIUM_POD_LABEL_SELECTOR = "app=debezium-server"
DEFAULT_SINK_POD_LABEL_SELECTOR = "app=cdc-sink"

SINK_POST_LINE_REGEX = re.compile(
    r"^(\S+)\s+(?:::ffff:)?(\d+\.\d+\.\d+\.\d+)\s.*POST / HTTP"
)
NANOSECOND_SUFFIX_REGEX = re.compile(r"(\.\d{6})\d*Z?$")


def kubectl(*args: str, raise_on_error: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(["kubectl", *args], capture_output=True, text=True)
    if raise_on_error and result.returncode != 0:
        raise RuntimeError(
            f"kubectl {' '.join(args)} failed (code {result.returncode}): "
            f"{result.stderr.strip()}"
        )
    return result


def get_active_debezium_pod_name(namespace: str, pod_label_selector: str) -> str:
    result = kubectl(
        "get", "pod", "-n", namespace, "-l", pod_label_selector,
        "-o", "jsonpath={.items[0].metadata.name}",
    )
    return result.stdout.strip()


def is_pod_ready(namespace: str, pod_name: str) -> bool:
    result = kubectl(
        "get", "pod", "-n", namespace, pod_name,
        "-o", 'jsonpath={.status.conditions[?(@.type=="Ready")].status}',
        raise_on_error=False,
    )
    return result.stdout.strip() == "True"


def get_pod_ip(namespace: str, pod_name: str) -> str:
    result = kubectl(
        "get", "pod", "-n", namespace, pod_name,
        "-o", "jsonpath={.status.podIP}",
        raise_on_error=False,
    )
    return result.stdout.strip()


def get_pod_age_seconds(namespace: str, pod_name: str) -> float:
    result = kubectl(
        "get", "pod", "-n", namespace, pod_name,
        "-o", "jsonpath={.status.startTime}",
    )
    start_time_iso = result.stdout.strip()
    if not start_time_iso:
        return 0.0
    start_dt = datetime.strptime(
        start_time_iso, "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - start_dt).total_seconds()


def get_pod_restart_count(namespace: str, pod_name: str) -> int:
    result = kubectl(
        "get", "pod", "-n", namespace, pod_name,
        "-o", "jsonpath={.status.containerStatuses[0].restartCount}",
    )
    return int(result.stdout.strip() or "0")


def parse_kubectl_timestamp(timestamp_string: str) -> float:
    """Convert a kubectl --timestamps prefix (RFC3339 with nanoseconds) to epoch seconds."""
    truncated = NANOSECOND_SUFFIX_REGEX.sub(r"\1+00:00", timestamp_string)
    if truncated.endswith("Z"):
        truncated = truncated[:-1] + "+00:00"
    return datetime.fromisoformat(truncated).timestamp()


def start_sink_post_event_streamer(
    namespace: str, sink_label_selector: str,
) -> tuple[subprocess.Popen, list]:
    """
    Spawn `kubectl logs -f --timestamps=true` on the sink pod and collect every
    POST access-log line as (timestamp_epoch_seconds, source_ip_string).
    """
    sink_logs_process = subprocess.Popen(
        ["kubectl", "logs", "-n", namespace, "-l", sink_label_selector,
         "--tail=0", "-f", "--timestamps=true"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, bufsize=1,
    )
    sink_post_events: list[tuple[float, str]] = []

    def reader_thread() -> None:
        for log_line in sink_logs_process.stdout:
            match = SINK_POST_LINE_REGEX.search(log_line)
            if not match:
                continue
            try:
                event_timestamp = parse_kubectl_timestamp(match.group(1))
                source_ip = match.group(2)
                sink_post_events.append((event_timestamp, source_ip))
            except Exception:
                pass

    threading.Thread(target=reader_thread, daemon=True).start()
    time.sleep(SINK_TAIL_ATTACH_SETTLE_SECONDS)
    return sink_logs_process, sink_post_events


def wait_for_warmup(namespace: str, pod_name: str, run_label: str) -> None:
    pod_age_seconds = get_pod_age_seconds(namespace, pod_name)
    pod_restart_count = get_pod_restart_count(namespace, pod_name)
    print(f"[run {run_label}] PRE pod={pod_name} "
          f"age={pod_age_seconds:.0f}s restarts={pod_restart_count}")
    if pod_restart_count > 0:
        print(f"[run {run_label}] ABORT: restart_count={pod_restart_count} > 0; "
              "rollout the deployment and retry")
        sys.exit(2)
    if pod_age_seconds < WARMUP_REQUIRED_SECONDS:
        sleep_seconds = int(WARMUP_REQUIRED_SECONDS - pod_age_seconds) + 1
        print(f"[run {run_label}] WARMUP sleep {sleep_seconds}s")
        time.sleep(sleep_seconds)


def wait_for_replacement_ready(
    namespace: str, deleted_pod_name: str, run_label: str, pod_label_selector: str,
) -> tuple[float, str, str]:
    deadline = time.time() + READY_POLL_TIMEOUT_SECONDS
    replacement_pod_ip = ""
    while time.time() < deadline:
        candidate_name = get_active_debezium_pod_name(namespace, pod_label_selector)
        if candidate_name and candidate_name != deleted_pod_name:
            if not replacement_pod_ip:
                replacement_pod_ip = get_pod_ip(namespace, candidate_name)
            if replacement_pod_ip and is_pod_ready(namespace, candidate_name):
                return time.time(), candidate_name, replacement_pod_ip
        time.sleep(READY_POLL_INTERVAL_SECONDS)
    print(f"[run {run_label}] TIMEOUT waiting for replacement pod to be Ready")
    sys.exit(3)


def wait_for_first_event_from_replacement(
    sink_post_events: list[tuple[float, str]],
    delete_timestamp: float,
    replacement_pod_ip: str,
    run_label: str,
) -> float:
    deadline = time.time() + FIRST_EVENT_POLL_TIMEOUT_SECONDS
    while time.time() < deadline:
        for event_timestamp, source_ip in sink_post_events:
            if event_timestamp > delete_timestamp and source_ip == replacement_pod_ip:
                return event_timestamp
        time.sleep(FIRST_EVENT_POLL_INTERVAL_SECONDS)
    print(f"[run {run_label}] TIMEOUT waiting for first event from {replacement_pod_ip}")
    sys.exit(4)


def measure_one_run(
    namespace: str, run_label: str,
    pod_label_selector: str, sink_label_selector: str,
) -> tuple[float, float]:
    pod_to_delete_name = get_active_debezium_pod_name(namespace, pod_label_selector)
    wait_for_warmup(namespace, pod_to_delete_name, run_label)

    sink_logs_process, sink_post_events = start_sink_post_event_streamer(
        namespace, sink_label_selector,
    )

    delete_timestamp = time.time()
    kubectl("delete", "pod", "-n", namespace, pod_to_delete_name,
            "--grace-period=0", "--force")
    print(f"[run {run_label}] DELETE_TS={delete_timestamp:.3f}")

    ready_timestamp, replacement_pod_name, replacement_pod_ip = (
        wait_for_replacement_ready(
            namespace, pod_to_delete_name, run_label, pod_label_selector,
        )
    )
    print(f"[run {run_label}] READY_TS={ready_timestamp:.3f} "
          f"replacement={replacement_pod_name} ip={replacement_pod_ip}")

    first_event_timestamp = wait_for_first_event_from_replacement(
        sink_post_events, delete_timestamp, replacement_pod_ip, run_label,
    )

    sink_logs_process.terminate()
    try:
        sink_logs_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        sink_logs_process.kill()

    time_to_ready_seconds = ready_timestamp - delete_timestamp
    time_to_first_event_seconds = first_event_timestamp - delete_timestamp

    print(f"[run {run_label}] time_to_ready={time_to_ready_seconds:.3f}s  "
          f"time_to_first_event={time_to_first_event_seconds:.3f}s")
    print(
        "CSV,"
        f"{namespace},{run_label},"
        f"{pod_to_delete_name},{replacement_pod_name},"
        f"{delete_timestamp:.3f},{ready_timestamp:.3f},{first_event_timestamp:.3f},"
        f"{time_to_ready_seconds:.3f},{time_to_first_event_seconds:.3f}"
    )
    return time_to_ready_seconds, time_to_first_event_seconds


def main(argv: list[str]) -> int:
    positional: list[str] = []
    pod_label_selector = DEFAULT_DEBEZIUM_POD_LABEL_SELECTOR
    sink_label_selector = DEFAULT_SINK_POD_LABEL_SELECTOR

    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg == "--pod-label-selector" and i + 1 < len(argv):
            pod_label_selector = argv[i + 1]
            i += 2
        elif arg == "--sink-label-selector" and i + 1 < len(argv):
            sink_label_selector = argv[i + 1]
            i += 2
        else:
            positional.append(arg)
            i += 1

    if len(positional) < 1:
        print(__doc__.strip(), file=sys.stderr)
        return 64
    target_namespace = positional[0]
    number_of_runs = int(positional[1]) if len(positional) > 1 else 1
    run_label_prefix = positional[2] if len(positional) > 2 else "run"

    for run_index in range(1, number_of_runs + 1):
        run_label = (
            f"{run_label_prefix}.{run_index}" if number_of_runs > 1 else run_label_prefix
        )
        print(f"\n=== RUN {run_index}/{number_of_runs} namespace={target_namespace} "
              f"pod={pod_label_selector!r} sink={sink_label_selector!r} ===")
        measure_one_run(
            target_namespace, run_label, pod_label_selector, sink_label_selector,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
