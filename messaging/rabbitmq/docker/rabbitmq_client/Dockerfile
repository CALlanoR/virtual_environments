FROM ubuntu:20.04

# Install pika
RUN apt-get clean
RUN mv /var/lib/apt/lists /var/lib/apt/lists.old
RUN mkdir -p lists/partial
RUN apt-get clean
RUN apt-get update
RUN apt-get -y install python python3-pip git vim iputils-ping
RUN pip install --upgrade pip
RUN pip3.8 install pika

RUN mkdir /home/workdir
WORKDIR /home/workdir 
