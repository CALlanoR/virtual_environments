#!/usr/bin/env bash
# Monitorea I/O del contenedor mysql-replica del stack mysql5.7.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "$SCRIPT_DIR/_common.sh"

CONTAINER="mysql-replica"
MYSQL_PORT=3307
STACK_LABEL="mysql5.7"

run_monitor "$@"
