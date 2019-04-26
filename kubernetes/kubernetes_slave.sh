#!/usr/bin/env bash

apt update

# Install Docker
apt install -y docker.io

# Enable Docker
systemctl enable docker

# Add the Kubernetes signing key
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add

# Install curl
apt install -y curl

# Add Xenial Kubernetes Repository
apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"

#  Install Kubeadm
apt install -y kubeadm

# Kubernetes Deployment
# Disable swap memory (if running)
swapoff -a

# Give Unique hostname
hostnamectl set-hostname slave-node