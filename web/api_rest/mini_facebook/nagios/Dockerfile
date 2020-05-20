FROM jasonrivers/nagios:latest

ENV NAGIOS_HOME /opt/nagios

RUN apt-get update
RUN apt-get install -y vim mc

COPY minifacebook.cfg /opt/nagios/etc/objects/
RUN tail -n 5 /opt/nagios/etc/nagios.cfg
COPY nagios.cfg ${NAGIOS_HOME}/etc/nagios.cfg

