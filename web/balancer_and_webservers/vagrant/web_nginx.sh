#!/usr/bin/env bash

apt-get update
apt-get install -y nginx
service nginx restart
sudo apt-get clean