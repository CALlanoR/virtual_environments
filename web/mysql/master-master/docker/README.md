## Taken from:
https://mysqlhighavailability.com/setting-up-mysql-group-replication-with-mysql-docker-images/

## Steps
1. sudo docker pull mysql/mysql-server:8.0
2. sudo docker images
3. sudo docker network create groupnet
4. sudo docker network ls

5. You need to decide whether to configure a single-primary or multi-primary mode. In a single primary configuration, MySQL always designates the first group member as the single primary server which will handle all write operations. A multi-primary mode allows writes to any of the group members.

# Running 3 Docker MySQL containers
for N in 1 2 3
do sudo docker run -d --name=node$N --net=groupnet --hostname=node$N \
  -v $PWD/d$N:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=mypass \
  mysql/mysql-server:8.0 \
  --server-id=$N \
  --log-bin='mysql-bin-1.log' \
  --enforce-gtid-consistency='ON' \
  --log-slave-updates='ON' \
  --gtid-mode='ON' \
  --transaction-write-set-extraction='XXHASH64' \
  --binlog-checksum='NONE' \
  --master-info-repository='TABLE' \
  --relay-log-info-repository='TABLE' \
  --plugin-load='group_replication.so' \
  --relay-log-recovery='ON' \
  --group-replication-start-on-boot='OFF' \
  --group-replication-group-name='aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee' \
  --group-replication-local-address="node$N:33061" \
  --group-replication-group-seeds='node1:33061,node2:33061,node3:33061' \
  --loose-group-replication-single-primary-mode='OFF' \
  --loose-group-replication-enforce-update-everywhere-checks='ON'
done

6. ls -la
7. sudo docker ps -a
8. sudo docker logs node1 

# Sleep for two seconds for servers to come online...

# Setting up and starting GR in the containers
# Execute these commands on node1 which will bootstrap the group:
9. sudo docker exec -it node1 mysql -uroot -pmypass \
  -e "SET @@GLOBAL.group_replication_bootstrap_group=1;" \
  -e "create user 'repl'@'%';" \
  -e "GRANT REPLICATION SLAVE ON *.* TO repl@'%';" \
  -e "flush privileges;" \
  -e "change master to master_user='repl' for channel 'group_replication_recovery';" \
  -e "START GROUP_REPLICATION;" \
  -e "SET @@GLOBAL.group_replication_bootstrap_group=0;" \
  -e "SELECT * FROM performance_schema.replication_group_members;"

# For node2 and node3, execute the below command:
10. for N in 2 3
do sudo docker exec -it node$N mysql -uroot -pmypass \
  -e "change master to master_user='repl' for channel 'group_replication_recovery';" \
  -e "START GROUP_REPLICATION;"
done

# Use the Performance Schema tables to monitor GR:
11. sudo docker exec -it node1 mysql -uroot -pmypass \
  -e "SELECT * FROM performance_schema.replication_group_members;"

# Adding some data
12. sudo docker exec -it node1 mysql -uroot -pmypass \
  -e "create database TEST; use TEST; CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY) ENGINE=InnoDB; show tables;"

# Let’s add some data by connecting to the other group members:
13. for N in 2 3
do sudo docker exec -it node$N mysql -uroot -pmypass \
  -e "INSERT INTO TEST.t1 VALUES($N);"
done

# Let’s see whether the data was inserted:
14. for N in 1 2 3
do sudo docker exec -it node$N mysql -uroot -pmypass \
  -e "SHOW VARIABLES WHERE Variable_name = 'hostname';" \
  -e "SELECT * FROM TEST.t1;"
done

# GR fault tolerance scenarios
Let’s start by creating and analysing GR behaviour if one of the nodes looses connectivity.

First, let’s set the option group_replication_exit_state_action to READ_ONLY, so node3 will not be killed when it goes to ERROR state.

When group_replication_exit_state_action is set to READ_ONLY, if the member exits the group unintentionally or exhausts its auto-rejoin attempts, the instance switches MySQL to super read only mode (by setting the system variable super_read_only to ON). This setting was the behavior for MySQL 8.0 releases before the system variable was introduced, and became the default again from MySQL 8.0.16. 

15. sudo docker exec -it node3 mysql -uroot -pmypass \
  -e "set @@global.group_replication_exit_state_action=READ_ONLY;"

# we can disconnect now node3 from the groupnet network by running:
16. sudo docker network disconnect groupnet node3

# Checking the group members:
17. for N in 1 3
do sudo docker exec -it node$N mysql -uroot -pmypass \
  -e "SHOW VARIABLES WHERE Variable_name = 'hostname';" \
  -e "SELECT * FROM performance_schema.replication_group_members;"
done

# Let’s reestablish the network connection in node3 and rejoin the node:
18. sudo docker network connect groupnet node3

# Rejoining node3:
19. sudo docker exec -it node3 mysql -uroot -pmypass \
  -e "STOP GROUP_REPLICATION; START GROUP_REPLICATION;"

# Checking the group members:
20. for N in 1 3
do sudo docker exec -it node$N mysql -uroot -pmypass \
  -e "SHOW VARIABLES WHERE Variable_name = 'hostname';" \
  -e "SELECT * FROM performance_schema.replication_group_members;"
done

# We can also stop or kill a node. Let’s kill node3:
21. sudo docker kill node3

# Run the command below to check the group members again:
22. sudo docker exec -it node1 mysql -uroot -pmypass \
  -e "SELECT * FROM performance_schema.replication_group_members;"

# Cleaning up: stopping containers, removing created network and image

23. To stop the running container(s):
sudo docker stop node1 node2 node3

# To remove the stopped container(s):
24. sudo docker rm node1 node2 node3

# To remove the data directories created (they are located in the folder where the containers were started from):
25. sudo rm -rf d1 d2 d3

# To remove the created network:
26. sudo docker network rm groupnet

# To remove the MySQL 8 image:
27. sudo docker rmi mysql/mysql-server:8.0