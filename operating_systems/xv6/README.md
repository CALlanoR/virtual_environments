# For ubuntu 20.04 and 22.04

### Install Docker Dependencies
```
$ sudo apt update
$ sudo apt install -y ca-certificates curl gnupg lsb-release
```

### Enable Docker Official Repository
```
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

$ echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### Install Docker with Apt Command

```
$ sudo apt-get update
$ sudo apt install docker-ce docker-ce-cli containerd.io -y
```

Once the docker package is installed, add your local user to docker group so that user can run docker commands without sudo
```
$ sudo usermod -aG docker $USER
$ newgrp docker
```

### Pull docker xv6 image
```
sudo docker pull grantbot/xv6
```

### Get xv6 sources from github
```
git clone https://github.com/CALlanoR/xv6-public.git
```

### Run xv6
```
sudo docker run -it -v <<ruta donde estan los fuentes>>:/xv6 grantbot/xv6:latest
cd xv6-public
make qemu-nox
wait for the prompt

ls
cat README

to exit of xv6: Ctrl A X
```
