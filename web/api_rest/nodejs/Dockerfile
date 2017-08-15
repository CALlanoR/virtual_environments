FROM ubuntu:14.04
MAINTAINER Carlos Llano

RUN apt-get update
RUN apt-get upgrade -y

# Install basic libraries
RUN apt-get install -y nano vim curl software-properties-common

# Install nodejs
RUN curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
RUN apt-get install -y nodejs

# Install MongoDB
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
RUN echo "deb [ arch=amd64 ] http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
RUN apt-get update
RUN apt-get install -y mongodb-org

RUN mkdir /home/todoListApi
RUN mkdir /data/db -p
CMD mongod

EXPOSE 3000
