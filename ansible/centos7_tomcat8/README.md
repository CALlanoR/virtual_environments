Docker container: CentOS 7 + Java 8 + Tomcat 8

## Build the image

```sh
sudo docker build -t centos7-tomcat8 .
```

## How to use (Quick use)

```sh
sudo docker images
sudo docker run -di -p 8080:8080 -p 5432:5432 --name=centos7_tomcat8 centos7-tomcat8
sudo docker exec -it centos7_tomcat8 bash
```


## How to use (with website)
Put your war under the `/opt/tomcat/webapps` directory and run the following command.
```sh
docker run -v /opt/tomcat/webapps:/opt/tomcat/webapps -v /opt/tomcat/logs:/opt/tomcat/logs -p 8080:8080 -p 5432:5432 -i -t --name centos7_tomcat8 centos7-tomcat8
```

Once you run it, you can start the container with `docker start centos7-tomcat8` in next time and log file will be under the `/opt/tomcat/logs` directory.

Also, if you got some error, you can remove the container with `docker rm centos7-tomcat8`. Your current container list will be show with `docker ps -a`.

For Mac user, you must share the directory `/opt/tomcat/webapps` and `/opt/tomcat/logs` on Docker > Preferences > File Sharing.

## Versions
If you got error while build the docker image, please check the latest version of Java and Tomcat.

|Software|Version|Note|
|:-----------|:------------|:------------|
|CentOS|7||
|Java|8u181|(https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)|
|Apache Tomcat|8.5.53|[Tomcat Download Page](http://apache.mirror.gtcomm.net/tomcat/tomcat-8/)|

[Docker Official Image for Tomcat](https://github.com/docker-library/tomcat) is also available.


## Some Dockerfiles source may be found here:

https://github.com/CentOS/CentOS-Dockerfiles
https://hub.docker.com/r/centos/postgresql/


## Launching PostgreSQL
Quick Start (not recommended for production use)
```sh
docker run --name=postgresql -d -p 5432:5432 <yourname>/postgresql
```

To connect to the container as the administrative postgres user:

```sh
docker run -it --rm --volumes-from=postgresql <yourname>/postgres sudo -u postgres -H psql
```

## Creating a database at launch
You can create a postgresql superuser at launch by specifying DB_USER and
DB_PASS variables. You may also create a database by using DB_NAME.

```sh
docker run --name postgresql -d \
-e 'DB_USER=username' \
-e 'DB_PASS=ridiculously-complex_password1' \
-e 'DB_NAME=my_database' \
<yourname>/postgresql
```

To connect to your database with your newly created user:

```sh
psql -U username -h $(docker inspect --format {{.NetworkSettings.IPAddress}} postgresql)
```