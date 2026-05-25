FROM debezium/connect:2.7.3.Final

USER root

# Descarga el plugin S3 Sink directamente desde Confluent Hub (sin necesitar confluent-hub CLI)
RUN curl -fsSL \
    "https://api.hub.confluent.io/api/plugins/confluentinc/kafka-connect-s3/versions/10.5.19/archive" \
    -o /tmp/kafka-connect-s3.zip \
    && unzip /tmp/kafka-connect-s3.zip -d /tmp/kafka-connect-s3 \
    && cp -r /tmp/kafka-connect-s3/confluentinc-kafka-connect-s3-*/lib /kafka/connect/kafka-connect-s3 \
    && rm -rf /tmp/kafka-connect-s3.zip /tmp/kafka-connect-s3

USER kafka
