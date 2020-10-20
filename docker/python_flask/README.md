
sudo docker build --tag=mini-amazon-users .
sudo docker image ls

sudo docker run -d -p 9090:9090 mini-amazon-users

