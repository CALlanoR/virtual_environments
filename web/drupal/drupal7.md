sudo docker pull mariadb
sudo docker pull drupal:7
sudo docker run -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_DATABASE=drupal7 -e MYSQL_USER=drupal7 -e MYSQL_PASSWORD=drupal7 -v mariadb:/var/lib/mysql -d --name mariadb mariadb
sudo docker run --name drupal7 --link mariadb:mysql -p 80:80 -d drupal:7

En el browser:
http://localhost/install.php