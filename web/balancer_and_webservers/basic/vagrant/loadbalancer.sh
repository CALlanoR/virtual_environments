#!/usr/bin/env bash

apt-get update
apt-get install -y haproxy
#=1.6.3-1ubuntu0.1
echo "ENABLED=1" > /etc/default/haproxy
mv /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.original

echo "
global
        log 127.0.0.1   local0
        log 127.0.0.1   local1 notice
        #log loghost    local0 info
        maxconn 4096
        #chroot /usr/share/haproxy
        user haproxy
        group haproxy
        daemon
        #debug
        #quiet

defaults
        log     global
        mode    http
        option  httplog
        option  dontlognull
        retries 3
        option redispatch
        maxconn 2000
        timeout connect      5000
        timeout client      50000
        timeout server      50000

listen website 
    bind 0.0.0.0:80
    mode http
    stats enable
    stats uri /haproxy?stats
    stats realm Strictly\ Private
    stats auth user1:password
    stats auth user2:password
    balance roundrobin
    option httpclose
    option forwardfor
    server webserver1 192.168.56.106:80 check
    server webserver2 192.168.56.107:80 check" > /etc/haproxy/haproxy.cfg

sudo apt-get clean
service haproxy restart



# #Steps for ubuntu 16.04

# #!/usr/bin/env bash

# apt-get update
# apt-get install -y haproxy openssh-server

# echo "ENABLED=1" >> /etc/default/haproxy

# mv /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.original

# echo "
# frontend firstbalance
#         bind *:80
#         option forwardfor
#         default_backend webservers

# backend webservers
#         balance roundrobin
#         server webserver1 192.168.56.120:80 check
#         server webserver2 192.168.56.121:80 check
#         option httpchk
# " >> /etc/haproxy/haproxy.cfg

# haproxy -f /etc/haproxy/haproxy.cfg -c

# sudo apt-get clean
# service haproxy restart
# service haproxy status
