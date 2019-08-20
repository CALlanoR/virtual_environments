## Hosting some simple static content

sudo docker build -t nginx_static .

sudo docker run --name some-nginx -p 70:80 -d nginx_static

## Documentation

https://hub.docker.com/_/nginx

