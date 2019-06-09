
How install mysql in ubuntu 16.04
=================================
https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-16-04
https://www.digitalocean.com/community/tutorials/how-to-install-the-latest-mysql-on-ubuntu-16-04


Test mysql with mysql workbench
===============================
Hostname: 192.168.56.120
username: root
password: root
Default Schema: myDB 

Test mysql service
==================
systemctl status mysql.service
mysqladmin --version

1. mysql -u root -p  # password in mysql.sh
2. show databases;
3. Basics:
	3.1. mysql -u root -p
	3.2. CREATE USER 'mrblue'@'localhost' IDENTIFIED BY 'Password123!';
		3.2.1. SELECT User,Host FROM mysql.user;
	3.3. CREATE DATABASE test;
	3.4. grant all privileges on test.* to 'mrblue'@'localhost';
	3.5. FLUSH PRIVILEGES;
	3.6. use test;
	3.7. mysql -h host -u mrblue -p test
	3.8. CREATE TABLE pet (name VARCHAR(20), owner VARCHAR(20), species VARCHAR(20), sex CHAR(1), birth DATE, death DATE);
	3.9. show tables;
	4.0. DESCRIBE pet;
	4.1. INSERT INTO pet VALUES ('Puffball','Diane','hamster','f','1999-03-30',NULL);
	4.2. select * from pet;

For more information: https://dev.mysql.com/doc/refman/5.7/en/tutorial.html
