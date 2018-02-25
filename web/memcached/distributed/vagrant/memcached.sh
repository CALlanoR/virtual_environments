#!/usr/bin/env bash

apt-get update

apt-get install -y memcached

sed -i "s/-l 127.0.0.1/-l 0.0.0.0/g" /etc/memcached.conf

/etc/init.d/memcached restart
