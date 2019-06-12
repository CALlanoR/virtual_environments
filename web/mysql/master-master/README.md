
## Master-Master replication
Master-Master replication, also known as mirror, is by far the simplest technique you can use to increase the performance and the reliability of your MySQL server installation. If you don’t know what it is, just imagine two MySQL server instances continuosly updating each other in real-time while fullfilling their job. In order to do that you’ll need a second machine/server, meaning you’ll have to sustain more costs: don’t make this stop you – an investment like that is hardly worthless: conversely, it will most likely be a substantial improvement for your system.

## Steps
Open two terminals and ssh in either Server mysql-master1 and Server mysql-master2<br />
`vagrant ssh mysql-masterX`

`sudo su`

`vi /etc/mysql/mysql.conf.d/mysqld.cnf`

# Updated the configuration
Under the mysqld section add or modify the following values in the server mysql-master1 (192.168.56.121):

[mysqld]<br />
server-id=1<br />
log-bin="mysql-bin"<br />
binlog-ignore-db=test<br />
binlog-ignore-db=information_schema<br />
replicate-ignore-db=test<br />
replicate-ignore-db=information_schema<br />
relay-log="mysql-relay-log"<br />
auto-increment-increment = 2<br />
auto-increment-offset = 1<br />

Under the mysqld section add or modify the following values in the server mysql-master2 (192.168.56.122):

[mysqld]<br />
server-id=2<br />
log-bin="mysql-bin"<br />
binlog-ignore-db=test<br />
binlog-ignore-db=information_schema<br />
replicate-ignore-db=test<br />
replicate-ignore-db=information_schema<br />
relay-log="mysql-relay-log"<br />
auto-increment-increment = 2<br />
auto-increment-offset = 2<br />

`Once you did that, you can stop the servers and restart them.`

# on both
sudo su<br />
mysql -u root -proot<br />
CREATE USER 'replicator'@'%' IDENTIFIED BY 'password123+';<br />
GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%' IDENTIFIED BY 'password123+';<br />

exit of each mysql prompt

# Test the connection of master1 to master2
mysql -u replicator -ppassword123+ -h 192.168.56.122 -P 3306

# Test the connection of master2 to master1
mysql -u replicator -ppassword123+ -h 192.168.56.121 -P 3306

exit of each mysql prompt


# Configure replication from master1 to master2
# in master1
mysql -u root -proot<br />
show master status; <br />

# in master2
mysql -u root -proot<br />
stop slave;<br />
CHANGE MASTER TO MASTER_HOST='192.168.56.121', MASTER_PORT=3306, MASTER_USER='replicator', MASTER_PASSWORD='password123+', MASTER_LOG_FILE='mysql-bin.000001', MASTER_LOG_POS = 1067;

`You should copy the values of MASTER_LOG_FILE and MASTER_LOG_POS that "SHOW MASTER STATUS" returns on Server master1.`

start slave;


# Configure replication from master2 to master1
# in master2
show master status;

# in master1
stop slave;<br />
CHANGE MASTER TO MASTER_HOST='192.168.56.122', MASTER_PORT=3306, MASTER_USER='replicator', MASTER_PASSWORD='password123+', MASTER_LOG_FILE='mysql-bin.000001', MASTER_LOG_POS = 1067;

`You should copy the values of MASTER_LOG_FILE and MASTER_LOG_POS that "SHOW MASTER STATUS" returns on Server master2.`

start slave;


## Test mysql service
Server master1:<br />
create table myDB.example (`id` varchar(10));<br />
insert into myDB.example values("1");<br />

Server master2:<br />
show tables in myDB;<br />
SELECT * FROM myDB.example;<br />
insert into myDB.example values("2");<br />


## For more information:
https://dev.mysql.com/doc/refman/5.7/en/tutorial.html<br />
https://www.ryadel.com/en/mysql-master-master-replication-setup-in-5-easy-steps/<br />
https://linode.com/docs/databases/mysql/configure-master-master-mysql-database-replication/
