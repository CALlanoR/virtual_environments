NodeJs official docker images
=============================
https://hub.docker.com/_/node/

Steps to create nodejs container
================================
1. Create image with nodejs and mongodb installed
sudo docker build -t nodejs_graphql_image .

2. Verify images
sudo docker images

3. Create server container
sudo docker run -di -p 127.0.0.1:4000:4000 --name=nodejs02 nodejs_graphql_image

4. Verify ip address of each container
sudo docker ps -a
sudo docker exec -it nodejs02 bash

5. Please follow the link below:
https://medium.com/codingthesmartway-com-blog/creating-a-graphql-server-with-node-js-and-express-f6dddc5320e1

Web page
========
http://graphql.org/

