#!/usr/bin/env bash

apt-get update
apt-get install nfs-server openssh-server build-essential mpich2 git -y

echo "127.0.0.1     localhost
192.168.56.111 hpcnode1
192.168.56.112 hpcnode2
192.168.56.113 hpcnode3" >> /etc/hosts

# store data and programs in this folder.
mkdir /mirror
echo "/mirror *(rw,sync)" | sudo tee -a /etc/exports

service nfs-kernel-server restart

# perl -e 'printf("%s\n", crypt("mpiu", "password"))'
useradd -m -p pakv0N1q//yG2 -s /bin/bash mpiu
echo 'mpiu	ALL=(ALL:ALL) ALL' >> /etc/sudoers

chown mpiu /mirror

echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

#sudo -u mpiu bash
#ssh-keygen -t rsa -b 2048 -f /home/mpiu/.ssh/id_rsa -C "Open MPI"

sudo mkdir /home/mpiu/.ssh
sudo touch /home/mpiu/.ssh/id_rsa
sudo touch /home/mpiu/.ssh/id_rsa.pub
sudo chmod 700 /home/mpiu/.ssh

echo "-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAn6Sk1oK7cowH/zCUXxCEerEg1y4dL8rMUs5+JQ+iJoDUxtd3
5bL3EadvAeaseFA9Mqfy5ICYLovczoag0TDBag9MFm/gkVmIHYGKoUuZfy3IMWZv
d4tV8waOJK6nT5WvGgjZILDeWA54MDHRRub1vI2HJBaeIcNVfDV/1UEkepjNKjiQ
+yixvj6YvouKxQY0pyf3AvQmFuEQeNuoUvdUoRt0zZofg0azyu3udMUxOidRanVz
1iRDZ85EWsp0ovQWJQMM0QQeTeFiR9aboYz3KLtxJ/M4r/RDcnHBmrVWWdcg8X75
wyGaz0KftvfbH2xJ4A4ASHh0OSYlx0wZ6EB5lQIDAQABAoIBADUvmyNERsLw2DEy
tBu/2wMtQ+2slVi4zb3AwdIDFViSj1D3tCA4sYuWJquReGBVCy53ObrbBNhtDFFa
FPXcsnNtSUIoX77M/0YlRFRcZXUzgYDDydsf9rCSvISIE4G2MrIPxJbZlhnsKCqW
Tky64Z/B3wYs6t4Av9gz0rTvkQGuo9r9xL1QFnsXQ0E41yT366kGHiCBwM/trSn2
ESxFPlVWTqIsQbYPMmGpw6UgeCrFQ4mBdIMeNf1ZWCibsQpqslTGIXduydwOIq5D
Oo30xHwRpSyx4AmAjW212X5mtU1CCL5rudqtqkNx6nN06HUlX2frJtilcxW+5Ndh
Souo/0ECgYEAz7SethhIYz0nqwXRKEzTeMDlttbN58bLTmBkxVZc/d2gcKKeun0A
iVR6doQaiql2MwFEzIFZ8g+yitVE9eodvPtfpuqaA720ip6ShSQDrtrI4dbm2bqW
8/GJVyXvSSkWIwXsA9G+cGxkK79wFIm/e37Z/ItM5DVT8btUaeS0BLkCgYEAxMMt
SUZLB0wYqOoiqTgrCP2qBoCd0jyvt0Qc/aUheOZFty1RCL8R/DW6b3DdVWoxtpEW
+d4IYENo+UIg/m15IIm0xXxrQtb+Q0Rc9VeURnEw2dvtqq9KPC2NgsVAIkuojqtv
CFieUWq49UyW/tz8yVipNQJR2+hQnRMYPI9cZb0CgYB0qITPz7mwi2OhSeYc1XGd
C/K5i9IgUOZVggx3TbdzGqyHNr8iDR1lBJ63vCDQKrfpk9fZaPlk3G4yTfCqkjDb
uPATZwbT/RPPG5s9zmmHJvjW54XHWmZ4Yvv5h6PrGnmFeEkEKCTnLenhLGe+EVQL
/8ZdcrvgHRel2Mpjo4F8eQKBgAhDKeOpz/y+dUqiilIQyb3W6Qzc2cO6SKapdY4x
IPaytLq8bGqxm0+78dg8JQ8xJmVEMnLLoA5qxj2xSTFl53A2WCDy2I41+PdaJ40l
4FQU7Lg5RAGm2rcsMoULQ2YtRya2jDMNhZhlot6qGK0bGoJZ9sEDF+zkFH6EDsB8
RKUBAoGBAKoX++URXLHBxUo5gRiowJfMLwALSN+4+ACO0l0HW7iqzwk4u7KWAbvY
n7IIIB1cQGIDG5djIx9BPCKdKBFD36TXbzKvDUdsusvNRaCeK/IhO2mWf9D/mXRE
uo6XKFedMl2lbz72qvqiBd9JwFcHFzaEai7JH5R445vrhS7mzUmU
-----END RSA PRIVATE KEY-----" > /home/mpiu/.ssh/id_rsa

sudo chmod 600 /home/mpiu/.ssh/id_rsa

echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCfpKTWgrtyjAf/MJRfEIR6sSDXLh0vysxSzn4lD6ImgNTG13flsvcRp28B5qx4UD0yp/LkgJgui9zOhqDRMMFqD0wWb+CRWYgdgYqhS5l/LcgxZm93i1XzBo4krqdPla8aCNkgsN5YDngwMdFG5vW8jYckFp4hw1V8NX/VQSR6mM0qOJD7KLG+Ppi+i4rFBjSnJ/cC9CYW4RB426hS91ShG3TNmh+DRrPK7e50xTE6J1FqdXPWJENnzkRaynSi9BYlAwzRBB5N4WJH1puhjPcou3En8ziv9ENyccGatVZZ1yDxfvnDIZrPQp+299sfbEngDgBIeHQ5JiXHTBnoQHmV Open MPI" > /home/mpiu/.ssh/id_rsa.pub

sudo cat /home/mpiu/.ssh/id_rsa.pub >> /home/mpiu/.ssh/authorized_keys
sudo chmod 600 /home/mpiu/.ssh/authorized_keys

sudo chown mpiu.mpiu /home/mpiu/.ssh -R

echo "hpcnode3:4  # this will spawn 4 processes on hpcnode3
hpcnode2:2  # this will spawn 2 processes on hpcnode2
hpcnode1    # this will spawn 1 process on hpcnode1
hpcmaster    # this will spawn 1 process on hpcmaster" > /home/mpiu/machinefile