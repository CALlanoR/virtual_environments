FROM python:3.7

RUN apt-get update
RUN apt-get install -y cron 

# install requirements (early and on their own to leverage caching)
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

WORKDIR /app

COPY daemon.py /app

# make script executable
RUN chmod +x /app/daemon.py

# Add crontab file in the cron directory  Probar con /dev/null 2>&1
RUN printf "* * * * * /usr/bin/python3 /app/daemon.py >> /var/log/cron.log 2>&1\n" >> /etc/cron.d/crontab

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/crontab

# Apply cron job
RUN crontab /etc/cron.d/crontab

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log

HEALTHCHECK --interval=5s --timeout=30s --retries=3 CMD cat /var/log/cron.log || exit 1
