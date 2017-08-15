#!/usr/bin/env bash

apt-get update
apt-get install -y haproxy
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
        contimeout      5000
        clitimeout      50000
        srvtimeout      50000

listen website 0.0.0.0:80
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