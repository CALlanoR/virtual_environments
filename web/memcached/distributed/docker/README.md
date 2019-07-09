# Link: https://memcached.org/

## Create memcached servers
sudo docker-compose up -d

## Install python client
sudo apt-get update

sudo apt-get install -y python3-dev
sudo apt-get install -y libmemcached-dev
sudo apt-get install -y libz-dev
export LC_ALL=C
sudo apt-get install -y python3-pip
sudo pip3 install pylibmc

python3 python_memcached_client.py


# Verify in each memcached server (in two terminals)

telnet localhost 11211

get ahmed

get tek

# in the second terminal
telnet localhost 11212

get ahmed

get tek


