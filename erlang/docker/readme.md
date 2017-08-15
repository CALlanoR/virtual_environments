

https://hub.docker.com/_/erlang/
sudo docker run -d --name erlang1 -it erlang
sudo docker ps -a
sudo docker exec -it <<ID>> bash


Old way
=======
sudo docker build -t erlang19.1.2 .
sudo docker run -ti -P --name erlang_docker erlang19.1.2
sudo docker ps -a
sudo docker inspect --format '{{ .NetworkSettings.IPAddress }}' <<ID>>
sudo docker exec -it <<ID>> bash
