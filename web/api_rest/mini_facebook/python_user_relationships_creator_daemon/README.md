1. Create image with python service installed
sudo docker build -t python_user_relationship_creator_deamon .

2. Verify images
sudo docker images

3. Create server container
sudo docker run -di --name=python_user_relationship_creator_deamon python_user_relationship_creator_deamon

4. Verify ip address of each container
sudo docker ps -a
sudo docker exec -it python_user_relationship_service bash

5. log
tail -f /var/log/cron.log