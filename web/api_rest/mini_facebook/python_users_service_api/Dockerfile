# A simple Flask app container.
FROM python:3.7

# Place app in container.
COPY . /opt/www
WORKDIR /opt/www

RUN sed -e s/localhost/MySQLServiceDB/ < /opt/www/db_config.py > /opt/www/db_config.py
RUN cat /opt/www/db_config.py

# Install dependencies.
RUN pip3 install -r requirements.txt

EXPOSE 5010