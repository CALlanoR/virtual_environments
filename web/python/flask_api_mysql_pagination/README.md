CORS = https://en.wikipedia.org/wiki/Cross-origin_resource_sharing

docker volume ls
docker volume rm put_here_the_name_of_the_volumes_related_to_this_project

docker-compose up -d

Verify that the containers are up

docker ps -a
docker start put_here_the_name_or_id_of_the_container

In your terminal execute:
python3 consumer/consumer.py
