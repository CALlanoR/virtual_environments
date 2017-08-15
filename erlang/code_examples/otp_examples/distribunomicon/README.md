
nodes (with docker containers)
==============================
sudo docker run -d --name erlang1 -it erlang
sudo docker run -d --name erlang2 --link erlang1:erlang1 -it erlang

sudo docker inspect --format '{{ .NetworkSettings.IPAddress }}' erlang1
sudo docker inspect --format '{{ .NetworkSettings.IPAddress }}' erlang2

In each container:
apt-get update
apt-get install vim

In each container to modify /etc/hosts to add the another container in this way:

root@1f7d9be487d0:/# cat /etc/hosts
127.0.0.1	localhost
::1	localhost ip6-localhost ip6-loopback
fe00::0	ip6-localnet
ff00::0	ip6-mcastprefix
ff02::1	ip6-allnodes
ff02::2	ip6-allrouters
172.17.0.3	erlang2 2afdda91c3b4
172.17.0.2	erlang1 1f7d9be487d0

In each node:

callanor@erlang1:~$ erl -name foo@172.17.0.2 -setcookie chat
Erlang/OTP 19 [erts-8.1] [source] [64-bit] [smp:2:2] [ds:2:2:10] [async-threads:10] [hipe] [kernel-poll:false] [sharing-preserving]


callanor@erlang2:~$ erl -name bar@172.17.0.3 -setcookie chat
Erlang/OTP 19 [erts-8.1] [source] [64-bit] [smp:2:2] [ds:2:2:10] [async-threads:10] [hipe] [kernel-poll:false] [sharing-preserving]

In erlang1 connect:

Eshell V9.0.1  (abort with ^G)
(foo@172.17.0.2)1> net_kernel:connect_node('bar@172.17.0.3').    
true
(foo@172.17.0.2)2> nodes().
['bar@172.17.0.3']
(foo@172.17.0.2)3>



nodes (with vagrant virtual machines)
=====================================
- erlang1:192.168.56.115
- erlang2:192.168.56.116

in erlang1 /etc/hosts add the another node:
192.168.56.116  erlang2.example.com     erlang2

in erlang2 /etc/hosts add the another node:
192.168.56.115  erlang1.example.com     erlang1

In each node:

callanor@erlang1:~$ erl -name foo@192.168.56.115 -setcookie chat
Erlang/OTP 19 [erts-8.1] [source] [64-bit] [smp:2:2] [ds:2:2:10] [async-threads:10] [hipe] [kernel-poll:false] [sharing-preserving]


callanor@erlang2:~$ erl -name bar@192.168.56.116 -setcookie chat
Erlang/OTP 19 [erts-8.1] [source] [64-bit] [smp:2:2] [ds:2:2:10] [async-threads:10] [hipe] [kernel-poll:false] [sharing-preserving]

In erlang 1 connect:

Eshell V8.1  (abort with ^G)
(foo@192.168.56.115)1> net_kernel:connect_node('bar@192.168.56.116').
true
(foo@192.168.56.115)2> nodes().
['bar@192.168.56.116']
(foo@192.168.56.115)3>
