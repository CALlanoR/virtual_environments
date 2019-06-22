
## Official page
https://hub.docker.com/_/mysql

# Start a mysql server instance
docker run --name some-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:tag

docker run --name myMySQL -e MYSQL_ROOT_PASSWORD=root -d mysql:5.7

... where some-mysql is the name you want to assign to your container, my-secret-pw is the password to be set for the MySQL root user and tag is the tag specifying the MySQL version you want. See the list above for relevant tags.

For more information to see the official page.

sudo docker inspect myMySQL

Get the ipAddress and use it in mysqlworkbench
