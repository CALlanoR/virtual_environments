# Build
sudo docker-compose build

sudo docker-compose up -d

python3 manual_tests.py | jq .


## Swagger documentation
https://dzone.com/articles/spring-boot-2-restful-api-documentation-with-swagg

http://localhost:7070/swagger-ui.html

## Manual
sudo docker run -d \
      -p 3306:3306 \
     --name mysql-server \
     -e MYSQL_ROOT_PASSWORD=root \
     -e MYSQL_DATABASE=db_example \
     -e MYSQL_USER=springuser \
     -e MYSQL_PASSWORD=ThePassword \
        mysql:5.7

docker build -f Dockerfile -t java-service .

docker run -t --name java-service --link mysql-server:mysql -p 8080:8080 java-service