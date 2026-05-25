-- Sintaxis MySQL 8.0.23+: CHANGE REPLICATION SOURCE TO + START REPLICA.
--
-- IMPORTANTE: NO pre-creamos el usuario `debezium` aquí. Las escrituras a
-- `mysql.user` se replican por defecto desde el primario, así que el usuario
-- llegará vía replicación. Si lo creáramos también aquí, el applier fallaría
-- al reproducir el CREATE USER del binlog (1396 — duplicate user).
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST          = 'mysql-primary',
  SOURCE_PORT          = 3306,
  SOURCE_USER          = 'repl',
  SOURCE_PASSWORD      = 'repl',
  SOURCE_AUTO_POSITION = 1,
  GET_SOURCE_PUBLIC_KEY = 1;

START REPLICA;
