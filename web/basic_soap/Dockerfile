FROM ubuntu:16.04
MAINTAINER Carlos Llano

RUN apt-get update
RUN apt-get install -y nano vim curl software-properties-common python-software-properties
RUN apt-get install openjdk-8-jdk -y
# RUN add-apt-repository ppa:webupd8team/java -y
# RUN apt-get update
# RUN echo oracle-java7-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections
# RUN apt-get install oracle-java8-installer -y
RUN apt-get clean

RUN mkdir /home/server /home/client
COPY server/Invoice.java /home/server
COPY server/ServiceInvoiceStarter.java /home/server
COPY client/InvoiceClient.java /home/client

EXPOSE 1212
