FROM ubuntu:14.04
MAINTAINER Carlos Llano

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y nano vim curl software-properties-common
RUN add-apt-repository ppa:webupd8team/java -y
RUN apt-get update
RUN echo oracle-java7-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections
RUN apt-get install -y oracle-java8-installer
RUN apt-get clean

RUN mkdir /home/server /home/client
COPY Invoice.java /home/server
COPY ServiceInvoiceStarter.java /home/server
COPY client/InvoiceClient.java /home/client

EXPOSE 1212
