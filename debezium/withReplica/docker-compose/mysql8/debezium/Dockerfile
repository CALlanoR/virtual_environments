# Debezium Server 3.x solo trae preempaquetados los conectores de Cassandra.
# Para usar el conector de MySQL hay que descargarlo y dejarlo en
# /debezium/connectors/debezium-connector-mysql/, junto con un
# extra_class_path.sh que lo añada al classpath cuando el run.sh detecta
# EXTRA_CONNECTOR=mysql.
#
# Build multi-stage porque la base de Debezium no incluye `gzip`.
ARG DEBEZIUM_VERSION=3.5.0.Final

FROM alpine:3.20 AS connector
ARG DEBEZIUM_VERSION
RUN apk add --no-cache curl tar \
 && mkdir -p /out \
 && curl -fsSL -o /tmp/mysql-connector.tar.gz \
      "https://repo1.maven.org/maven2/io/debezium/debezium-connector-mysql/${DEBEZIUM_VERSION}/debezium-connector-mysql-${DEBEZIUM_VERSION}-plugin.tar.gz" \
 && tar -xzf /tmp/mysql-connector.tar.gz -C /out/ \
 && printf 'export EXTRA_CLASS_PATH="$EXTRA_CONNECTOR_DIR/*"$PATH_SEP\n' \
      > /out/debezium-connector-mysql/extra_class_path.sh \
 && chmod -R a+rX /out/debezium-connector-mysql

FROM quay.io/debezium/server:${DEBEZIUM_VERSION}
COPY --from=connector --chown=jboss:root /out/debezium-connector-mysql /debezium/connectors/debezium-connector-mysql
ENV EXTRA_CONNECTOR=mysql
