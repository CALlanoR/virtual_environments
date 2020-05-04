# A simple Flask app container.
FROM python:3.7
MAINTAINER Carlos Llano <callano@javerianacali.edu.co>

WORKDIR /app

# Place app in container.
COPY publications_consumer/consumer.py .

# Install dependencies.
RUN pip3 install -r requirements.txt

# Without this setting, Python never prints anything out.
ENV PYTHONUNBUFFERED=1

CMD ["python", "/app/consumer.py"]