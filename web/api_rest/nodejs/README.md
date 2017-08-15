Documentation links
===================
- https://nodejs.org/en/download/package-manager/
- https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/


1. Create image with nodejs and mongodb installed
sudo docker build -t nodejs_mongodb_image .

2. Verify images
sudo docker images

3. Create server container
sudo docker run -di -p 127.0.0.1:3000:3000 --name=nodejs01 nodejs_mongodb_image

4. Verify ip address of each container
sudo docker ps -a
sudo docker inspect --format '{{ .NetworkSettings.IPAddress }}' <<ID>>
sudo docker exec -it <<ID>> bash

5. Please follow the link below:
https://www.codementor.io/olatundegaruba/nodejs-restful-apis-in-10-minutes-q0sgsfhbd
Note:
- Install npm install --save body-parser
- Install in Chrome a rest client e.g: postman
