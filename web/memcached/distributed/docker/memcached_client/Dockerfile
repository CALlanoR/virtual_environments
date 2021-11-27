FROM ubuntu:18.04

# Install wget and gnupg2
RUN apt-get update

RUN apt-get install -y wget gnupg2 python3 python3-dev 


RUN apt-get install -y libmemcached-dev libz-dev python3-pip
RUN export LC_ALL=C
RUN pip3 install pylibmc


# Add script
ADD python_memcached_client.py /tmp/python_memcached_client.py
