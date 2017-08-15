#!/usr/bin/env bash

# Install nfs
sudo apt-get update
sudo apt-get install nfs-client openssh-server build-essential mpich2 git -y

echo "127.0.0.1     localhost
192.168.56.110 hpcmaster" >> /etc/hosts

# perl -e 'printf("%s\n", crypt("mpiu", "password"))'
useradd -m -p pakv0N1q//yG2 -s /bin/bash mpiu
echo 'mpiu	ALL=(ALL:ALL) ALL' >> /etc/sudoers

# store data and programs in this folder.
sudo mkdir /mirror

sudo mount hpcmaster:/mirror /mirror

echo "hpcmaster:/mirror    /mirror    nfs" | sudo tee -a /etc/fstab
sudo mount -a

#sudo chown mpiu.mpiu /mirror

sudo mkdir /home/mpiu/.ssh

# Append master key into authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCfpKTWgrtyjAf/MJRfEIR6sSDXLh0vysxSzn4lD6ImgNTG13flsvcRp28B5qx4UD0yp/LkgJgui9zOhqDRMMFqD0wWb+CRWYgdgYqhS5l/LcgxZm93i1XzBo4krqdPla8aCNkgsN5YDngwMdFG5vW8jYckFp4hw1V8NX/VQSR6mM0qOJD7KLG+Ppi+i4rFBjSnJ/cC9CYW4RB426hS91ShG3TNmh+DRrPK7e50xTE6J1FqdXPWJENnzkRaynSi9BYlAwzRBB5N4WJH1puhjPcou3En8ziv9ENyccGatVZZ1yDxfvnDIZrPQp+299sfbEngDgBIeHQ5JiXHTBnoQHmV Open MPI" > /home/mpiu/.ssh/authorized_keys

sudo chmod 700 /home/mpiu/.ssh
sudo chmod 600 /home/mpiu/.ssh/authorized_keys
sudo chown mpiu.mpiu /home/mpiu/.ssh -R