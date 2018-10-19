sudo apt-get update
sudo apt-get purge lxc-docker
sudo apt-get install -y linux-image-extra-´$(uname -r)´
sudo apt-get install -y docker-engine
sudo service docker start

echo "Creating nginx image..."
sudo docker build -t nginx_server_image .

echo "Creating nginx server container..."
sudo docker run -d -P --name=nginx_server nginx_server_image

echo "Checking ssh port..."
sudo docker port nginx_server 22

echo "Obtaining container id..."
ID="$(sudo docker inspect --format '{{ .Id }}' nginx_server)"
echo "Container id: $ID"

echo "Obtaining container ip address..."
IP="$(sudo docker inspect --format '{{ .NetworkSettings.IPAddress }}' $ID)"
echo "IP address: $IP"
echo "login with: ssh root@$IP, password is root, please change it."
