
Run this command to download the latest version of Docker Compose:

https://docs.docker.com/compose/install/

sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose


docker-rabbitmq example:

Docker example: RabbitMQ with python + pika

Run this:

```
sudo docker-compose up --scale rabbitmq_client=2 -d
```

sudo docker ps -a
docker_rabbitmq_client_1
docker_rabbitmq_client_2
docker_rabbitmq_server

Create two terminals and execute this command in each one:

sudo docker exec -ti docker_rabbitmq_client_1 bash
sudo docker exec -ti docker_rabbitmq_client_2 bash

into the first linux terminal to do:

1. cd publish_subscribe
2. python consumer_logs.py

into the second linux terminal to do:

1. cd publish_subscribe
2. python publish_logs.py


sudo docker-compose stop

sudo docker-compose rm

http://localhost:15672

if is running in vagrant: http://192.168.56.120:15672


https://www.rabbitmq.com/vhosts.html



sudo curl -L https://github.com/docker/compose/releases/download/1.18.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo docker-compose --version


docker stack deploy --compose-file docker-compose.yml vossibility

docker node ps $(docker node ls -q)