sudo docker build --tag=friendlyhello .
sudo docker image ls
sudo docker run -p 4000:80 friendlyhello
http://localhost:4000/

sudo docker run -d -p 4000:80 friendlyhello
