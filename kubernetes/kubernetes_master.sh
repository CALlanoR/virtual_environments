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
hostnamectl set-hostname master-node

# Initialize Kubernetes on the master node
kubeadm init --pod-network-cidr=10.244.0.0/16
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config

# Deploy a Pod Network through the master node
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml


