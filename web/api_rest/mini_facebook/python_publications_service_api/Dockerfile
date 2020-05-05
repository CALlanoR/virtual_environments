
# A simple Flask app container.
FROM python:3
MAINTAINER Carlos Llano <callano@javerianacali.edu.co>

# Place app in container.
COPY . /opt/www
WORKDIR /opt/www

RUN sed '0,/localhost/{s/localhost/rabbitMQService/}' < /opt/www/db_config.py > /opt/www/db_config.py
RUN sed '0,/localhost/{s/localhost/mongoservicedb/}' < /opt/www/db_config.py > /opt/www/db_config.py
RUN cat /opt/www/db_config.py

# Install dependencies.
RUN pip3 install -r requirements.txt

EXPOSE 5010

