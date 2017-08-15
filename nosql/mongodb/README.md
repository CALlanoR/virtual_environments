Official image
https://hub.docker.com/_/mongo/
https://api.mongodb.com/python/current/tutorial.html

1. Create mongo server:
sudo docker run --name mongodb_server -p 27017:27017 -d mongo:3.5

2. Connect to it from an application
sudo docker run -itd --name mongodb_client --link mongodb_server ubuntu:14.04 /bin/bash

3 Install curl into the mongodb_client
sudo docker exec -ti mongodb_client bash
apt-get update
apt-get install -y curl vim nano

3.1 Install pip to download the mongodb python library
curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
python3 get-pip.py

pip install pymongo==3.4.0

3.2 Copy mongodb_test.py in mongodb_client and execute it.
