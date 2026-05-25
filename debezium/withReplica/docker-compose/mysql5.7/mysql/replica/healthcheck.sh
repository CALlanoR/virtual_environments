#!/bin/sh
# Healthcheck del contenedor mysql-replica.
# Verifica que (a) MySQL responde, (b) ambos hilos de replicación están corriendo.
set -e

mysqladmin ping --silent -h localhost -uroot -proot >/dev/null

status=$(mysql -uroot -proot -e 'SHOW SLAVE STATUS\G' 2>/dev/null)

echo "$status" | grep -q 'Slave_IO_Running: Yes'
echo "$status" | grep -q 'Slave_SQL_Running: Yes'
