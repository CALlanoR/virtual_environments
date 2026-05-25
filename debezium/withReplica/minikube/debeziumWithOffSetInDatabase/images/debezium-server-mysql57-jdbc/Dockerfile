# Imagen custom para el stack cdc-mysql57.
# La imagen oficial debezium/server:2.4.2.Final NO empaca debezium-storage-jdbc.
# Este Dockerfile la extiende y agrega ese JAR al classpath (/debezium/lib/),
# habilitando JdbcOffsetBackingStore y JdbcSchemaHistory en una versión 2.4.x
# del server (la imagen oficial 3.x ya lo trae preempaquetado).
#
# Build/load desde minikube/Makefile (targets image-build-57, image-load-57).
ARG DEBEZIUM_VERSION=2.4.2.Final

FROM alpine:3.20 AS storage-jar
ARG DEBEZIUM_VERSION
RUN apk add --no-cache curl \
 && mkdir -p /out \
 && curl -fsSL -o /out/debezium-storage-jdbc.jar \
      "https://repo1.maven.org/maven2/io/debezium/debezium-storage-jdbc/${DEBEZIUM_VERSION}/debezium-storage-jdbc-${DEBEZIUM_VERSION}.jar" \
 && chmod a+r /out/debezium-storage-jdbc.jar

FROM debezium/server:${DEBEZIUM_VERSION}
ARG DEBEZIUM_VERSION
COPY --from=storage-jar --chown=jboss:root \
     /out/debezium-storage-jdbc.jar \
     /debezium/lib/debezium-storage-jdbc-${DEBEZIUM_VERSION}.jar
