
## How install mysql in ubuntu 16.04
https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-16-04<br />
https://www.digitalocean.com/community/tutorials/how-to-install-the-latest-mysql-on-ubuntu-16-04

## Test mysql with mysql workbench
Hostname: 192.168.56.120<br />
username: root<br />
password: root<br />
Default Schema: myDB<br />

## Test mysql service
systemctl status mysql.service<br />
mysqladmin --version<br />

1. mysql -u root -p  # password in mysql.sh<br />
2. show databases;<br />
3. Basics:<br />
	3.1. mysql -u root -p<br />
	3.2. CREATE USER 'mrblue'@'localhost' IDENTIFIED BY 'Password123!';<br />
		3.2.1. SELECT User,Host FROM mysql.user;<br />
	3.3. CREATE DATABASE test;<br />
	3.4. grant all privileges on test.* to 'mrblue'@'localhost';<br />
	3.5. FLUSH PRIVILEGES;<br />
	3.6. use test;<br />
	3.7. mysql -h host -u mrblue -p test<br />
	3.8. CREATE TABLE pet (name VARCHAR(20), owner VARCHAR(20), species VARCHAR(20), sex CHAR(1), birth DATE, death DATE);<br />
	3.9. show tables;<br />
	4.0. DESCRIBE pet;<br />
	4.1. INSERT INTO pet VALUES ('Puffball','Diane','hamster','f','1999-03-30',NULL);<br />
	4.2. select * from pet;<br />

## For more information:
https://dev.mysql.com/doc/refman/5.7/en/tutorial.html
