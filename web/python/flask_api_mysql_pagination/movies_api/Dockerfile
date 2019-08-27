# A simple Flask app container.
FROM python:3
MAINTAINER Carlos Llano <callano@javerianacali.edu.co>

# Place app in container.
COPY . /opt/www
WORKDIR /opt/www

# Install dependencies.
RUN apt-get update && apt-get install jq vim nano curl -y
RUN pip3 install -r requirements.txt

EXPOSE 5000
