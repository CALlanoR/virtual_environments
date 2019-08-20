FROM redis
MAINTAINER Carlos Llano

RUN apt-get update
RUN apt install -y python3-pip
RUN pip3 install redis

RUN mkdir /home/workdir
COPY redis_test.py /home/workdir
WORKDIR /home/workdir

EXPOSE 6379

