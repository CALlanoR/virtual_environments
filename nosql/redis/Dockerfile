FROM redislabs/rejson
MAINTAINER Carlos Llano

RUN apt-get update
RUN apt install -y python3-pip vim
RUN pip3 install redis rejson

RUN mkdir /home/workdir
COPY redis_test.py /home/workdir
COPY redis_json_test.py /home/workdir
WORKDIR /home/workdir

EXPOSE 6379

