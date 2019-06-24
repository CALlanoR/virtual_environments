#!/usr/bin/env bash

apt-get update
apt-get install -y haproxy=1.6.3-1ubuntu0.2
apt-get install -y keepalived=1:1.2.24-1ubuntu0.16.04.2

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
    server webserver1 192.168.56.120:80 check
    server webserver2 192.168.56.121:80 check" > /etc/haproxy/haproxy.cfg

echo "net.ipv4.ip_nonlocal_bind=1" >> /etc/sysctl.conf
sysctl -p

echo "
! Configuration File for keepalived

global_defs {
   notification_email {
     sysadmin@mydomain.com
     support@mydomain.com
   }
   notification_email_from lb1@mydomain.com
   smtp_server localhost
   smtp_connect_timeout 30
}

vrrp_instance VI_1 {
    state MASTER
    interface enp0s8
    virtual_router_id 101
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    virtual_ipaddress {
        192.168.56.99
    }
}" > /etc/keepalived/keepalived.conf

/etc/init.d/keepalived restart
ip addr show enp0s8

sudo apt-get clean
service haproxy restart