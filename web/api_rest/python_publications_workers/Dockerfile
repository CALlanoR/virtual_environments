# A simple Flask app container.
FROM python:3.7
MAINTAINER Carlos Llano <callano@javerianacali.edu.co>

WORKDIR /app

# Place app in container.
COPY . /app

# Install dependencies.
RUN pip3 install -r requirements.txt

CMD celery worker --app=purplelab.celery.setup  --maxtasksperchild=1 -c 4 -l info -Ofair
