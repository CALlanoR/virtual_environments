# POC — Debezium + Kafka KRaft + S3 Sink

## Archivos
- `Dockerfile`             — extiende debezium/connect con el plugin S3 Sink
- `docker-compose.yml`     — stack completo (MySQL + Kafka KRaft + Debezium Connect)
- `connector-s3-sink.json` — conector S3 Sink (se registra via API REST)

---

## 1. Variables de entorno AWS

Crea un archivo `.env` en el mismo directorio (nunca lo subas a git):

```bash
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
```

---

## 2. Levantar el stack

```bash
# Construye la imagen con el plugin S3 Sink y levanta todo
docker compose up --build -d

# Verificar que Debezium Connect esté listo (esperar ~30s)
curl -s http://localhost:8083/ | jq .
```

---

## 3. Registrar el conector MySQL (Debezium)

```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mysql-source-connector",
    "config": {
      "connector.class":                "io.debezium.connector.mysql.MySqlConnector",
      "tasks.max":                      "1",
      "database.hostname":              "mysql-source",
      "database.port":                  "3306",
      "database.user":                  "root",
      "database.password":              "root_password",
      "database.server.id":             "1",
      "database.server.name":           "heimdall",
      "database.include.list":          "inventory",
      "database.history.kafka.bootstrap.servers": "kafka:9092",
      "database.history.kafka.topic":   "schema-changes.inventory",
      "include.schema.changes":         "true"
    }
  }'
```

---

## 4. Registrar el conector S3 Sink

```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @connector-s3-sink.json
```

---

## 5. Verificar conectores activos

```bash
curl -s http://localhost:8083/connectors | jq .

# Estado de un conector específico
curl -s http://localhost:8083/connectors/s3-sink-bronze/status | jq .

curl -s http://localhost:8083/connectors/mysql-source-connector/status | jq .
```

---

## 6. Resultado en S3

Los eventos se escriben en:
```
s3://llano-debezium-test-0001/
  bronze/events/heimdall.inventory.products/
    year=2026/month=04/day=13/hour=14/
      heimdall.inventory.products+0+0000000000.json
```

El archivo se cierra cada 60 segundos (`rotate.interval.ms=60000`)
o al llegar a 10.000 eventos (`flush.size=10000`), lo que ocurra primero.

---

## 7. Destruir todo
```bash
docker compose down --rmi all
```

## 8. Insertar datos en mysql

```sql
CREATE TABLE inventory.products (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

INSERT INTO inventory.products (name, description, price, stock) VALUES
('Laptop Dell XPS 15', 'Potente laptop para profesionales creativos', 1499.99, 15),
('Mouse Logitech MX Master 3', 'Mouse ergonómico de alta precisión', 79.99, 150),
('Teclado mecánico Keychron K2', 'Teclado compacto con switches Gateron', 89.99, 85),
('Monitor LG 27'' 4K', 'Monitor Ultra HD con colores vibrantes', 349.99, 30),
('Webcam Logitech C920', 'Cámara Full HD 1080p para streaming', 59.99, 200);
```

## 9. Connect to mysql via cli
```bash
docker exec -it mysql_source mysql -uroot -proot_password inventory

user: root
password: root_password
database: inventory
```

## 10. Validar Variables de ambiente AWS
```bash
(docker compose config | grep AWS
```

# View logs in debezium
```bash
docker logs -f debezium_server
```

## Notas para producción

- Reemplazar credenciales AWS por IAM Role (ECS Task Role) — eliminar las variables
  `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` del compose.
- Cambiar `format.class` a `io.confluent.connect.s3.format.parquet.ParquetFormat`
  para mejor compresión y rendimiento en Athena.
- Ajustar `rotate.interval.ms` a 300000 (5 min) o más según volumen real.
- Para múltiples MySQL, agregar un conector MySQL por cada base en el paso 3
  y actualizar `topics` en el S3 Sink con patrón: `"topics.regex": "srv-ccc.*"`.
