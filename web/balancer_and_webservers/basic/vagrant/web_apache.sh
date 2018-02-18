#!/usr/bin/env bash

apt-get update
apt-get install -y apache2
service nginx restart
sudo apt-get clean
