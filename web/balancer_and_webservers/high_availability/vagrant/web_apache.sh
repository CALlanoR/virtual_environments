#!/usr/bin/env bash

apt-get update
apt-get install -y apache2
service apache2 restart
sudo apt-get clean
