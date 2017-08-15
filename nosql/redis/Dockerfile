FROM ubuntu:14.04
MAINTAINER Carlos Llano

RUN apt-get update
RUN apt-get install -y redis-server

RUN apt-get install -y curl
RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
RUN python3.4 get-pip.py
RUN pip install redis

RUN mkdir /home/workdir
COPY redis_test.py /home/workdir
WORKDIR /home/workdir

EXPOSE 6379
ENTRYPOINT ["/usr/bin/redis-server"]
