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


10. We can also create a second version of our awesome app. Let’s change the code a little bit (let’s add some exclamation marks at the end):

var http = require('http');
var os = require('os');

http.createServer(function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/html'});
    res.end(`<h1>I'm ${os.hostname()}!!!</h1>`);
}).listen(8080);


11. So we need to build the image again, but this time it’s the second version of the app so we’ll write 
sudo docker build -t awesome:v2 .

12. To update our containers in the awesome service to use the v2 version of our app (without stop the service) we’ll write 
sudo docker service update --image awesome:v2 prod_awesome

13. if we want to scale the service to more than 20 containers, we can do it with only one command: 
sudo docker service scale prod_awesome=50

