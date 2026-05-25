#!/usr/bin/env bash
# Monitorea I/O del contenedor mysql8-replica del stack mysql8.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "$SCRIPT_DIR/_common.sh"

CONTAINER="mysql8-replica"
MYSQL_PORT=3309
STACK_LABEL="mysql8"

run_monitor "$@"
