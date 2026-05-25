-- Usuario para la réplica clásica primary→replica.
CREATE USER 'repl'@'%' IDENTIFIED BY 'repl';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';

-- Usuario que usará Debezium Server para conectarse y leer binlogs.
-- Aunque Debezium se conecta a la réplica, creamos el usuario también
-- aquí para que se replique a la réplica vía replicación de privilegios.
CREATE USER 'debezium'@'%' IDENTIFIED BY 'dbz';
GRANT REPLICATION SLAVE, REPLICATION CLIENT, SELECT, RELOAD ON *.* TO 'debezium'@'%';

FLUSH PRIVILEGES;
