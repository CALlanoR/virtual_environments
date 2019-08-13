
1. sudo docker run -d -p 127.0.0.1:81:80 -p 127.0.0.1:444:443 --name secure_nginx -i my-nginx
2. sudo docker ps -a
3. sudo docker exec -ti secure_nginx bash
4. /etc/init.d/nginx start
5. Verify in your local browser:
    - http://localhost:81
    - https://localhost:444
6. The following instructions describe how set up nginx with ssl certificate: https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-on-centos-7
7. Restart nginx: /etc/init.d/nginx restart
    Output:
    nginx: [warn] "ssl_stapling" ignored, issuer certificate not found
    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    nginx: configuration file /etc/nginx/nginx.conf test is successful

    Notice the warning in the beginning. As noted earlier, this particular setting throws a warning since our self-signed certificate can't use SSL stapling. This is expected and our server can still encrypt connections correctly.

8. Verify in your local browser:
    - https://localhost:444

NOTE
====
Use this example for ssl.conf file.
server {
    listen 443 http2 ssl;
    listen [::]:443 http2 ssl;

    server_name localhost;

    ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;
    ssl_dhparam /etc/ssl/certs/dhparam.pem;

    ########################################################################
    # from https://cipherli.st/                                            #
    # and https://raymii.org/s/tutorials/Strong_SSL_Security_On_nginx.html #
    ########################################################################

    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;
    ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
    ssl_ecdh_curve secp384r1;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    # Disable preloading HSTS for now.  You can use the commented out header line that includes
    # the "preload" directive if you understand the implications.
    #add_header Strict-Transport-Security "max-age=63072000; includeSubdomains; preload";
    add_header Strict-Transport-Security "max-age=63072000; includeSubdomains";
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;

    ##################################
    # END https://cipherli.st/ BLOCK #
    ##################################

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }

    #error_page  404              /404.html;

    # redirect server error pages to the static page /50x.html
    #
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }
}
