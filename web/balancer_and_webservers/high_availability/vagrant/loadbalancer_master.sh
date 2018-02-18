#!/usr/bin/env bash

apt-get update
apt-get install -y haproxy
apt-get install -y keepalived
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
    server webserver1 192.168.56.120:80 check
    server webserver2 192.168.56.121:80 check" > /etc/haproxy/haproxy.cfg


echo "net.ipv4.ip_nonlocal_bind=1" >> /etc/sysctl.conf
sysctl -p

echo "
vrrp_script chk_haproxy {           # Requires keepalived-1.1.13
        script "killall -0 haproxy"     # cheaper than pidof
        interval 2                      # check every 2 seconds
        weight 2                        # add 2 points of prio if OK
}

vrrp_instance VI_1 {
        interface eth1
        state MASTER
        virtual_router_id 51
        priority 101                    # 101 on master, 100 on backup
        virtual_ipaddress {
            192.168.56.99
        }
        track_script {
            chk_haproxy
        }
}" > /etc/keepalived/keepalived.conf

/etc/init.d/keepalived start

sudo apt-get clean
service haproxy restart