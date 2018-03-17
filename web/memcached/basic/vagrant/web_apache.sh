#!/usr/bin/env bash

apt-get update

apt-get install -y nginx
/etc/init.d/nginx start


apt-get -y install php7.0-fpm


echo "server {
    listen 192.168.56.120:80;
 
    root /var/www/html;
    index index.php index.html index.htm index.nginx-debian.html;
 
    server_name web1.example.com;
 
    location / {
        try_files $uri $uri/ =404;
    }
 
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
 
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php7.0-fpm.sock;
    }
 
    location ~ /\.ht {
        deny all;
    }
}" > /etc/nginx/sites-available/default

service nginx reload

sed -i "s/;cgi.fix_pathinfo=1/cgi.fix_pathinfo=0/g" /etc/php/7.0/fpm/php.ini

service php7.0-fpm reload


apt-get install -y php-memcached memcached

echo "<?php
$mem = new Memcached();
$mem->addServer(\"127.0.0.1\", 11211);

$result = $mem->get(\"blah\");


if ($result) {
    echo $result;
} else {
    echo \"No matching key found yet. Let's start adding that now!\";
    $mem->set(\"blah\", \"I am data!  I am held in memcached!\") or die(\"Couldn't save anything to memcached...\");
}
?>" > /var/www/html/cache_test.php

echo "<?php
phpinfo();
?>" > /var/www/html/index.php


service nginx reload
service php7.0-fpm reload
/etc/init.d/memcached restart
