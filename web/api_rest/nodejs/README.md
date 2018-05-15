For Dockerfile2 to do this:
===========================

Modules
=======

NodeJS
------
Installers are available for both Windows and macOS at https://nodejs.org/en/download/. 

Npm
---
Node.js eases support to third-party open source-developed modules by providing npm. It allows you, as a developer, to easily install, manage, and even provide your own module packages.

Express framework
-----------------
It is a flexible web application framework for Node.js, providing a robust RESTful API for developing single or multi-page web applications. 

Nodeunit
--------
it provides basic assert test functions for creating basic unit tests as well as tools for executing them.

nodejs http
-----------
Node.js HTTP module to start listening for incoming requests on port X.


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



Handling HTTP requests
======================
1. create the file hello-node-http-server.js and put this code on it:

var http = require('http');
var port = 8180;

function handleGetRequest(response) {
  response.writeHead(200, {'Content-Type' : 'text/plain'});
  response.end('Get action was requested');
}

function handlePostRequest(response) {
  response.writeHead(200, {'Content-Type' : 'text/plain'});
  response.end('Post action was requested');
}

function handlePutRequest(response) {
  response.writeHead(200, {'Content-Type' : 'text/plain'});
  response.end('Put action was requested');
}

function handleDeleteRequest(response) {
  response.writeHead(200, {'Content-Type' : 'text/plain'});
  response.end('Delete action was requested');
}

function handleBadRequest(response) {
  console.log('Unsupported http mehtod');
  response.writeHead(400, {'Content-Type' : 'text/plain'  });
  response.end('Bad request');
}

function handleRequest(request, response) {
  switch (request.method) {
    case 'GET':
      handleGetRequest(response);
      break;
    case 'POST':
      handlePostRequest(response);
      break;
    case 'PUT':
      handlePutRequest(response);
      break;
    case 'DELETE':
      handleDeleteRequest(response);
      break;
    default:
      handleBadRequest(response);
      break;
  }
  console.log('Request processing completed');
}

http.createServer(handleRequest).listen(8180, '0.0.0.0', () => {
  console.log('Started Node.js http server at http://0.0.0.0:8180');
});

9. run with node hello-node-http-server.js

10. In your local navigator install https://www.getpostman.com/ or restclient

11. Send different http verbs


Modularizing code
=================
1. create the directory modules and into create the file http-module.js and put the code above to
handle the requests

function handleGetRequest(response) {
  response.writeHead(200, {'Content-Type' : 'text/plain'});
  response.end('Get action was requested');
}

function handlePostRequest(response) {
  response.writeHead(200, {'Content-Type' : 'text/plain'});
  response.end('Post action was requested');
}

function handlePutRequest(response) {
  response.writeHead(200, {'Content-Type' : 'text/plain'});
  response.end('Put action was requested');
}

function handleDeleteRequest(response) {
  response.writeHead(200, {'Content-Type' : 'text/plain'});
  response.end('Delete action was requested');
}

function handleBadRequest(response) {
  console.log('Unsupported http mehtod');
  response.writeHead(400, {'Content-Type' : 'text/plain'  });
  response.end('Bad request');
}

exports.handleRequest = function(request, response) {
  switch (request.method) {
    case 'GET':
      handleGetRequest(response);
      break;
    case 'POST':
      handlePostRequest(response);
      break;
    case 'PUT':
      handlePutRequest(response);
      break;
    case 'DELETE':
      handleDeleteRequest(response);
      break;
    default:
      handleBadRequest(response);
      break;
  }
  console.log('Request processing completed');
}

2. create the file main.js

var http = require('http');
var port = 8180;

var httpModule = require('./modules/http-module');

http.createServer(httpModule.handleRequest).listen(8180, '0.0.0.0', () => {
  console.log('Started Node.js http server at http://127.0.0.1:8180');
});


Building a Typical Web API
==========================
Our first draft API will be a read-only version and will not support creating or updating items in the catalog as real-world applications do. Instead, we will concentrate on the API definition itself
Our first draft API will be a read-only version and will not support creating or updating items in the catalog as real-world applications do. Instead, we will concentrate on the API definition itself.


1. Specifying the API
=====================
Method URI Description
GET /category Retrieves all available categories in the catalog.
GET /category/{category-id}/ Retrieves all the items available under a specific category.
GET /category/{category-id}/{item-id} Retrieves an item by its ID under a specific category.
POST /category Creates a new category; if it exists, it will update it.
POST /category/{category-id}/ Creates a new item in a specified category. If the item exists, it will update it.
PUT /category/{category-id} Updates a category.
PUT/category/{category-id}/{item-id} Updates an item in a specified category.
DELETE/category/{category-id} Deletes an existing category.
DELETE/category/{category-id}/{item-id} Deletes an item in a specified category.

2. To choose an appropriate format
==================================
JSON objects are natively supported by JavaScript. They are easy to extend during the evolution of an application and are consumable by almost any platform available. Examples:

{ 
    "itemId": "item-identifier-1", 
    "itemName": "Sports Watch", 
    "category": "Watches", 
    "categoryId": 1,
    "price": 150, 
    "currency": "EUR"
} 

{
    "categoryName" : "Watches",
    "categoryId" : "1",
    "itemsCount" : 100,
    "items" : [{
            "itemId" : "item-identifier-1",
            "itemName":"Sports Watch",
            "price": 150,
            "currency" : "EUR"    
     }]
}




For Dockerfile to do this:
==========================
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
sudo docker exec -it nodejs01 bash

5. Please follow the link below:
https://www.codementor.io/olatundegaruba/nodejs-restful-apis-in-10-minutes-q0sgsfhbd
Note:
- Install npm install --save body-parser
- Install in Chrome a rest client e.g: postman
