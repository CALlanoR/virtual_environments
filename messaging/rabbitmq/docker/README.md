
Run this command to download the latest version of Docker Compose:

sudo curl -L https://github.com/docker/compose/releases/download/1.21.2/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose


docker-rabbitmq example:

Docker example: RabbitMQ with python + pika

Run this:

```
sudo docker-compose up -d
```

sudo docker ps -a
docker_rabbitmq_client_1
docker_rabbitmq_server_1

Create two terminals and execute this command in each one:

sudo docker exec -ti docker_rabbitmq_client_1 bash

into the first linux terminal to do:

1. cd publish_subscribe
2. python consumer_logs.py

into the second linux terminal to do:

1. cd publish_subscribe
2. python publish_logs.py