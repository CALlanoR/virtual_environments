#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y curl nano docker.io
apt-get install -y docker-compose
apt-get install -y make
apt-get install -y build-essential
apt-get install -y manpages-dev
apt-get install -y vim

# For Operating System
apt-get install -y gcc
apt-get install -y libncurses5-dev
apt-get install -y bison
apt-get install -y flex
apt-get install -y libssl-dev
apt-get install -y libelf-dev
apt-get update
apt-get upgrade -y

apt clean && sudo apt autoremove -y