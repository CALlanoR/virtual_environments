# A simple Flask app container.
FROM python:3.6
MAINTAINER Carlos Llano <callano@javerianacali.edu.co>

# Place app in container.
COPY . /opt/www
WORKDIR /opt/www

# Install dependencies.
RUN pip3 install -r requirements.txt

EXPOSE 5000
