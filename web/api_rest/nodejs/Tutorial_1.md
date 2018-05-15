Simple test (Setting up a development environment)
==================================================
Steps to create nodejs container
================================
1. Create image with nodejs installed
sudo docker build -t nodejs_image -f Dockerfile2 .

2. Verify images
sudo docker images

3. Create server container
sudo docker run -di -p 127.0.0.1:8180:127.0.0.1:8180 --name=nodejs02 nodejs_image

4. Verify ip address of each container
sudo docker ps -a
sudo docker exec -it nodejs02 bash

5. mkdir hello_node
6. cd hello_node
7. npm init

note: A command-line interaction wizard will ask you for your project name, its version, as well as some other metadata such as Git repository, your name, and so on, and will finally preview the package.json file it is to generate; when complete, your first Node.js project is ready to begin.

8. cat package.json

create the file hello-node.js and put this code on it:

var http = require('http');
http.createServer((request, response) => {  
	response.writeHead(200, {    
		'Content-Type' : 'text/plain'  
	});  
	response.end('Hello from Node.JS');
	console.log('Hello handler requested')
;}).listen(8180, '0.0.0.0', () => {  
	console.log('Started Node.js http server at http://0.0.0.0:8180');
});

9. run with node hello-node.js

10. In your local navigator put: http://127.0.0.1:8180/