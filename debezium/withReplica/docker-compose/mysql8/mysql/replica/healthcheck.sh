#!/bin/sh
# Healthcheck del contenedor mysql-replica (MySQL 8.0+).
# Verifica que (a) MySQL responde, (b) ambos hilos de replicación están corriendo.
# Sintaxis 8.0+: SHOW REPLICA STATUS y campos Replica_IO_Running / Replica_SQL_Running.
set -e

mysqladmin ping --silent -h localhost -uroot -proot >/dev/null

status=$(mysql -uroot -proot -e 'SHOW REPLICA STATUS\G' 2>/dev/null)

echo "$status" | grep -q 'Replica_IO_Running: Yes'
echo "$status" | grep -q 'Replica_SQL_Running: Yes'
