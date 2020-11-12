FROM ubuntu:18.04

RUN apt-get clean
RUN apt-get update
RUN apt-get -y install python3.8 python3-pip git vim iputils-ping
RUN pip3 install --upgrade pip
RUN pip3 install pika

RUN mkdir /home/workdir
COPY examples /home/workdir
WORKDIR /home/workdir 
