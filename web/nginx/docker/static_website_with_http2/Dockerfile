FROM nginx

COPY nginx.conf /etc/nginx/nginx.conf

COPY nginx.key /ssl/nginx.key
COPY nginx.crt /ssl/nginx.crt

COPY ./website/ /usr/share/nginx/html

RUN ls -la /usr/share/nginx/html

EXPOSE 80
EXPOSE 443