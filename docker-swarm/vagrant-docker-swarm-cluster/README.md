https://jazz-twk.medium.com/learn-docker-swarm-with-vagrant-47dd52b57bcc

# Start all machines with Vagrant
```
vagrant up
vagrant status
```

# Login into manager01 with the following command and verify Docker
```
vagrant ssh manager01
docker info
```

# Init Docker Swarm in manager01
```
docker swarm init --listen-addr 172.20.20.11:2377 --advertise-addr 172.20.20.11:2377
```

You will get the output, the command and token will be used to join the worker, record it somewhere to be used later.

Run the following command to get the token to join manager

```
docker swarm join-token manager
```

You will get the output, record the command and together with the token


# Add Manager02 into manager node

Open another terminal and login into manager02 machine, and run the command you copy from manager01 to join as a manager node

```
vagrant ssh manager02

take this command from the one generated in the previous step:

docker swarm join --token SWMTKN-1-17qbb6xqfsf90c2814a87faphesw0iztgncxum4ogs94mcnaz2-8gc05tc4bwwh4odbat6lynylm 172.20.20.11:2377
```


# Add Worker01, Worker02 into worker node
Now we will add worker node into Docker Swarm, use the worker token command from manager01 and run the command in worker01 machine.

```
vagrant ssh worker01 (Repeat for worker02)
```

use the output of the command executed in manager01 to add a node

```
docker swarm join --token SWMTKN-1-3mmo7ri90iygekk3aadyawygp51rpghka4bj3f8xdwsbulwcwz-cor2yt0f442rptzf02jgjfdhe 172.20.20.11:2377

```

run the following command in manager node to list all nodes
```
docker node ls
```

Repeat the same process in worker02 to join as worker node

```
vagrant ssh worker02
```

use the output of the command executed in manager01 to add a node

```
docker swarm join --token SWMTKN-1-3mmo7ri90iygekk3aadyawygp51rpghka4bj3f8xdwsbulwcwz-cor2yt0f442rptzf02jgjfdhe 172.20.20.11:2377

```

run the following command in manager node to list all nodes
```
docker node ls
```

Congratulations, you have a fully functioning Docker Swarm cluster.


# Deploy Portainer
Portainer is the simple and lightweight Docker management tool, we will deploy Portainer to visualize all our application status in our cluster. In Docker Swarm, all the provisioning must be executed in the manager node. 

Login into manager01 or manager02 and run the following command.

```
curl -L https://downloads.portainer.io/portainer-agent-stack.yml -o portainer-agent-stack.yml

docker stack deploy --compose-file=portainer-agent-stack.yml portainer
```

As we are deploying our containers into the distributed node, we cannot use the normal docker ps to check all container, you can use another simple command to list all containers from all nodes docker node ps $(docker node ls -q) .


```
navigate to http://localhost:9000/#/swarm/visualizer to visualize all your applications.
```

Portainer is the simple and lightweight Docker management tool, we will deploy Portainer to visualize all our application status in our cluster. In Docker Swarm, all the provisioning must be executed in the manager node. Login into manager01 or manager02 and run the following command.
