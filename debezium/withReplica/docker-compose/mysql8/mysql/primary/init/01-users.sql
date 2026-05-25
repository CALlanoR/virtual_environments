-- En MySQL 8.0 el plugin por defecto es caching_sha2_password. Para mantener
-- conexiones simples (sin negociar la public key vía SSL), creamos los usuarios
-- explícitamente con mysql_native_password.

CREATE USER 'repl'@'%' IDENTIFIED WITH mysql_native_password BY 'repl';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';

CREATE USER 'debezium'@'%' IDENTIFIED WITH mysql_native_password BY 'dbz';
GRANT REPLICATION SLAVE, REPLICATION CLIENT, SELECT, RELOAD ON *.* TO 'debezium'@'%';

FLUSH PRIVILEGES;
