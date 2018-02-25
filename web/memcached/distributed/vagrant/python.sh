#!/usr/bin/env bash

apt-get update

apt-get install -y python3-dev
apt-get install -y libmemcached-dev
apt-get install -y libz-dev
export LC_ALL=C
apt-get install -y python3-pip
pip3 install pylibmc

echo "
import pylibmc
mc = pylibmc.Client([\"192.168.56.121:11211\", 
                     \"192.168.56.122:11211\"], 
                    binary=True, 
                    behaviors={\"tcp_nodelay\": True, 
                               \"ketama\": True,
                               \"remove_failed\":1,
                               \"retry_timeout\": 1,
                               \"dead_timeout\": 60})
mc[\"ahmed\"] = \"Hello World\"
mc[\"tek\"] = \"Hello World\"
print (mc[\"ahmed\"])" >> /home/ubuntu/test_memcached.py

# restart machine
shutdown -r now