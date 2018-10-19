Serving multiple web apps using HAProxy and Docker containers
=============================================================

## Quick Start

## Install docker-compose (check this link to get the last version: https://github.com/docker/compose/releases/):
1. sudo curl -L https://github.com/docker/compose/releases/download/1.23.0-rc3/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
2. sudo chmod +x /usr/local/bin/docker-compose
3. sudo docker-compose -v 

## Build the web application
4. sudo docker build -t webnode .

## Build the environment
5. sudo docker swarm init
6. sudo docker stack deploy --compose-file=docker-compose.yml prod
7. sudo docker ps -a
8. curl http://localhost
9. sudo docker service ls


Reference: https://medium.com/@nirgn/load-balancing-applications-with-haproxy-and-docker-d719b7c5b231
