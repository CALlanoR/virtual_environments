FROM ubuntu:16.04
MAINTAINER Carlos Llano <carlos_llano@hotmail.com>

################################################################################
# Install requirements: git, jq, python
################################################################################
RUN apt-get update
RUN apt-get -y install vim git jq curl sudo wget rsyslog
RUN apt-get -y install python python-pip npm nodejs
RUN apt-get -y install software-properties-common apt-transport-https
RUN pip install --upgrade pip

################################################################################
# Install osquery and python bindings
################################################################################
RUN export OSQUERY_KEY=1484120AC4E9F8A1A577AEEE97A80C63C9D8B80B
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 1484120AC4E9F8A1A577AEEE97A80C63C9D8B80B
RUN add-apt-repository 'deb [arch=amd64] https://pkg.osquery.io/deb deb main' 
RUN apt-get update 
RUN apt-get -y install osquery
COPY osquery.example.conf /etc/osquery/osquery.conf

RUN mkdir /home/workdir
WORKDIR /home/workdir 
RUN git clone https://github.com/sidorares/osquery-node.git
RUN git clone https://github.com/osquery/osquery-python.git
#RUN mv osquery-node/ /home/workdir/
#RUN mv osquery-python/ /home/workdir/

COPY examples/execute_query.js /home/workdir/
COPY examples/execute_query.py /home/workdir/

################################################################################
# Install osquery and nodejs and python bindings
################################################################################
RUN npm install osquery
RUN pip install osquery
