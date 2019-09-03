CORS = https://en.wikipedia.org/wiki/Cross-origin_resource_sharing

List de volumes: `docker volume ls` <br/>
Delete volume: `docker volume rm put_here_the_name_of_the_volumes_related_to_this_project` <br/>

Deploy the services: `docker-compose up -d`

Verify that the containers are up: `docker ps -a` <br/>
Start containers: `docker start put_here_the_name_or_id_of_the_container`

Note: to configurate mysql workbench: `docker inspect MySQLMoviesDB` and get the field `IPAddress` at the end of the json output.

In your terminal execute: `python3 consumer/consumer.py`
