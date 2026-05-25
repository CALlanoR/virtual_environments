CREATE DATABASE IF NOT EXISTS inventory;
USE inventory;

-- Tabla INCLUIDA en table.include.list de Debezium.
CREATE TABLE customers (
  id          INT          NOT NULL AUTO_INCREMENT,
  first_name  VARCHAR(100) NOT NULL,
  last_name   VARCHAR(100) NOT NULL,
  email       VARCHAR(150) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;

INSERT INTO customers (first_name, last_name, email) VALUES
  ('Ada',     'Lovelace',  'ada@example.com'),
  ('Alan',    'Turing',    'alan@example.com'),
  ('Grace',   'Hopper',    'grace@example.com');

-- Tabla NO INCLUIDA: control negativo para validar el filtrado de Debezium.
-- Cualquier cambio aquí NO debe aparecer en los logs de debezium-server.
CREATE TABLE audit_log (
  id        INT          NOT NULL AUTO_INCREMENT,
  message   VARCHAR(255) NOT NULL,
  created_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB;

INSERT INTO audit_log (message) VALUES
  ('seed: stack initialized');
