FROM ubuntu:16.04
MAINTAINER Carlos Llano <carlos_llano@hotmail.com>

# Install pika
RUN apt-get clean
RUN mv /var/lib/apt/lists /var/lib/apt/lists.old
RUN mkdir -p lists/partial
RUN apt-get clean
RUN apt-get update
RUN apt-get -y install python python-pip git vim iputils-ping
RUN pip install --upgrade pip
RUN pip install pika

RUN mkdir /home/workdir
COPY examples /home/workdir
WORKDIR /home/workdir 
