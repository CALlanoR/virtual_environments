-- Sintaxis MySQL 5.7: CHANGE MASTER TO + START SLAVE.
-- (En MySQL 8.0.23+ los equivalentes son CHANGE REPLICATION SOURCE TO / START REPLICA.)
--
-- IMPORTANTE: NO pre-creamos el usuario `debezium` aquí. Las escrituras a
-- `mysql.user` se replican por defecto desde el primario, así que el
-- usuario llegará vía replicación. Si lo creáramos también aquí, el SQL
-- thread fallaría con error 1396 ("Operation CREATE USER failed") cuando
-- intente reproducir el CREATE USER del binlog del primario, ya que en
-- MySQL 5.7 la sentencia replicada NO lleva IF NOT EXISTS.
CHANGE MASTER TO
  MASTER_HOST          = 'mysql-primary',
  MASTER_PORT          = 3306,
  MASTER_USER          = 'repl',
  MASTER_PASSWORD      = 'repl',
  MASTER_AUTO_POSITION = 1;

START SLAVE;
