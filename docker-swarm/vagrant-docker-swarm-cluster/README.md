https://jazz-twk.medium.com/learn-docker-swarm-with-vagrant-47dd52b57bcc

1. vagrant up
2. vagrant status

Login into manager01 with the following command and verify Docker
3. vagrant ssh manager01
4. docker info

Login into manager01 with the following command and verify Docker
5. docker swarm init --listen-addr 172.20.20.11:2377 --advertise-addr 172.20.20.11:2377

the command and token will be used to join the worker, record it somewhere to be used later.

```
vagrant@manager01:~$ docker swarm init --listen-addr 172.20.20.11:2377 --advertise-addr 172.20.20.11:2377
Swarm initialized: current node (zcw11ild3wwplzewgm2nzy583) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join --token SWMTKN-1-5bfgf20pg1kaexy4iol3jwzq6rynjbu3rfy43d3tlsfn2zfvg7-5bkyo0ba0idduq9dac4el3vbu 172.20.20.11:2377

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
```


Run the following command to get the token to join manager
6. docker swarm join-token manager

You will get the following output, record the command and together with the token

```
vagrant@manager01:~$ docker swarm join-token manager
To add a manager to this swarm, run the following command:

    docker swarm join --token SWMTKN-1-5bfgf20pg1kaexy4iol3jwzq6rynjbu3rfy43d3tlsfn2zfvg7-6vmyweds8mpsyekxfbazifrvr 172.20.20.11:2377
```

Add Manager02 into manager node
Open another terminal and login into manager02 machine, and run the command you copy from manager01 to join as a manager node
7. vagrant ssh manager02

```
docker swarm join --token SWMTKN-1-5bfgf20pg1kaexy4iol3jwzq6rynjbu3rfy43d3tlsfn2zfvg7-6vmyweds8mpsyekxfbazifrvr 172.20.20.11:2377
```


Add Worker01, Worker02 into worker node
8. vagrant ssh worker01 (Repeat for worker02)

```
docker swarm join --token SWMTKN-1-5bfgf20pg1kaexy4iol3jwzq6rynjbu3rfy43d3tlsfn2zfvg7-6vmyweds8mpsyekxfbazifrvr 172.20.20.11:2377
```

in manager node to list all nodes (manager01)
9. docker node ls

Congratulations, you have a fully functioning Docker Swarm cluster.


Deploy Portainer

Portainer is the simple and lightweight Docker management tool, we will deploy Portainer to visualize all our application status in our cluster. In Docker Swarm, all the provisioning must be executed in the manager node. Login into manager01 or manager02 and run the following command.

http://172.20.20.11:15672/