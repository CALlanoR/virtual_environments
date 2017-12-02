Create cluster
==============
sudo docker-compose -d up

To scale the workers:
docker-compose scale spark-worker=2


Notes
=====
To use pyspark is necessary to install python.

The linux image is Alpine linux so the package manager is apk.

Steps:
apk update && \
apk upgrade && \
apk add git python


Documentation
=============
Docker-compose is based in this link:
https://hub.docker.com/r/gradiant/spark/

https://geekytheory.com/apache-spark-que-es-y-como-funciona/
http://spark.apache.org/docs/latest/quick-start.html
https://geekytheory.com/como-crear-un-cluster-de-servidores-con-apache-spark/
