## Hosting some simple static content with http2 configured

## Create certificates

openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout nginx.key -out nginx.crt

## Create image

sudo docker build -t nginx_with_http2 .

sudo docker run --name some-nginx-http2 -p 443:443 -p 80:80 -d nginx_with_http2

## Documentation

https://hub.docker.com/_/nginx

