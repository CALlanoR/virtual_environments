
How install mysql in ubuntu 16.04
=================================
https://linode.com/docs/databases/mysql/configure-master-master-mysql-database-replication/


Test mysql service
==================
Server 1:
create database test;
create table test.flowers (`id` varchar(10));

Server 2:
show tables in test;

For more information: https://dev.mysql.com/doc/refman/5.7/en/tutorial.html
