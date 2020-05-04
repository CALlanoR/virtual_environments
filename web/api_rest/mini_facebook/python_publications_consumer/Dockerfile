# A simple Flask app container.
FROM python:3.7
MAINTAINER Carlos Llano <callano@javerianacali.edu.co>

WORKDIR /app

# Place app in container.
COPY publications_consumer/consumer.py .
COPY requirements.txt .
COPY publications_consumer/config.ini .

RUN sed '0,/localhost/{s/localhost/rabbitMQService/}' < config.ini > config.ini
RUN sed '0,/localhost/{s/localhost/mongoservicedb/}' < config.ini > config.ini
RUN cat config.ini

# Install dependencies.
RUN pip3 install -r requirements.txt

# Without this setting, Python never prints anything out.
ENV PYTHONUNBUFFERED=1

CMD ["python3.7", "/app/consumer.py"]