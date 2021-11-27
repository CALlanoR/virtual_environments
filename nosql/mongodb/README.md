Official image
https://hub.docker.com/_/mongo/
https://api.mongodb.com/python/current/tutorial.html

1. Create mongo server:
sudo docker run --name mongodb_server -p 27017:27017 -d mongo:5.0

2. Connect to it from an application
sudo docker run -itd --name mongodb_client --link mongodb_server ubuntu:18.04 /bin/bash

3 Install curl into the mongodb_client
sudo docker exec -ti mongodb_client bash
apt-get update
apt-get install -y curl vim nano python3

3.1 Install pip to download the mongodb python library
apt-get install -y python3-pip

pip3 install pymongo==3.12.1

3.2 Copy mongodb_test.py in mongodb_client and execute it.
