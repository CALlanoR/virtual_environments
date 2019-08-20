1. Create the docker image
sudo docker build -t redis_image .

2. Create the container
sudo docker run -di -p 127.0.0.1:6379:6379 --name=redis01 redis_image

3. Verify ip address of each container
sudo docker ps -a
sudo docker inspect --format '{{ .NetworkSettings.IPAddress }}' <<ID>>
sudo docker exec -it <<ID>> bash

4. Check if Redis is working
redis-cli ping
PONG

6. in /home/workdir exec python3 redis_test.py
