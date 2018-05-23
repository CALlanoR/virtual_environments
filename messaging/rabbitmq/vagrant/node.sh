#!/usr/bin/env bash

# Install pika
sudo apt-get update
sudo apt-get install python-pip git -y
sudo pip install pika

# export LC_ALL="en_US.UTF-8"
# export LC_CTYPE="en_US.UTF-8"
# sudo dpkg-reconfigure locales

# sudo pip install --upgrade pip