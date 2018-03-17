#!/bin/bash

# Download and Install the Latest Updates for the OS
apt-get update && apt-get upgrade -y

# Set the Server Timezone to CST
echo "America/Chicago" > /etc/timezone
# dpkg-reconfigure -f noninteractive tzdata

# # Enable Ubuntu Firewall and allow SSH & MySQL Ports
# ufw enable
# ufw allow 22
# ufw allow 3306

# # Install essential packages
# apt-get -y install zsh htop

# echo "Installing MySQL 5.7 now..."

# LOGFILE=/tmp/install_log.txt

# echo "mysql-server-5.7 mysql-server/root_password password root" | sudo debconf-set-selections
# echo "mysql-server-5.7 mysql-server/root_password_again password root" | sudo debconf-set-selections
# apt-get -y install mysql-server-5.7 mysql-client >> $LOGFILE 2>&1



export DEBIAN_FRONTEND=noninteractive

MYSQL_ROOT_PASSWORD='callanor' # SET THIS! Avoid quotes/apostrophes in the password, but do use lowercase + uppercase + numbers + special chars

# Install MySQL
# Suggestion from @dcarrith (http://serverfault.com/a/830352/344471):
echo debconf mysql-server/root_password password $MYSQL_ROOT_PASSWORD | sudo debconf-set-selections
echo debconf mysql-server/root_password_again password $MYSQL_ROOT_PASSWORD | sudo debconf-set-selections
#sudo debconf-set-selections <<< "mysql-server-5.7 mysql-server/root_password password $MYSQL_ROOT_PASSWORD"
#sudo debconf-set-selections <<< "mysql-server-5.7 mysql-server/root_password_again password $MYSQL_ROOT_PASSWORD"
sudo apt-get -qq install mysql-server-5.7 > /dev/null # Install MySQL quietly

# Install Expect
sudo apt-get -qq install expect > /dev/null

# Build Expect script
tee ~/secure_our_mysql.sh > /dev/null << EOF
spawn $(which mysql_secure_installation)

expect "Enter password for user root:"
send "$MYSQL_ROOT_PASSWORD\r"

expect "Press y|Y for Yes, any other key for No:"
send "y\r"

expect "Please enter 0 = LOW, 1 = MEDIUM and 2 = STRONG:"
send "2\r"

expect "Change the password for root ? ((Press y|Y for Yes, any other key for No) :"
send "n\r"

expect "Remove anonymous users? (Press y|Y for Yes, any other key for No) :"
send "y\r"

expect "Disallow root login remotely? (Press y|Y for Yes, any other key for No) :"
send "y\r"

expect "Remove test database and access to it? (Press y|Y for Yes, any other key for No) :"
send "y\r"

expect "Reload privilege tables now? (Press y|Y for Yes, any other key for No) :"
send "y\r"

EOF

# Run Expect script.
# This runs the "mysql_secure_installation" script which removes insecure defaults.
sudo expect ~/secure_our_mysql.sh

# Cleanup
rm -v ~/secure_our_mysql.sh # Remove the generated Expect script
#sudo apt-get -qq purge expect > /dev/null # Uninstall Expect, commented out in case you need Expect

echo "MySQL setup completed. Insecure defaults are gone. Please remove this script manually when you are done with it (or at least remove the MySQL root password that you put inside it."

echo "Configuring master #2 in /etc/mysql/my.cnf"

echo "
[mysqld]
server_id                = 2
log_bin                  = /var/log/mysql/mysql-bin.log
log_bin_index            = /var/log/mysql/mysql-bin.log.index
relay_log                = /var/log/mysql/mysql-relay-bin
relay_log_index          = /var/log/mysql/mysql-relay-bin.index
expire_logs_days         = 10
max_binlog_size          = 100M
log_slave_updates        = 1
auto-increment-increment = 2
auto-increment-offset    = 1
bind-address             = 192.168.56.121" >> /etc/mysql/my.cnf

service mysql restart

# pseudo-user that will be used for replicating data between our two VPS. IP address of the opposing Linode.
mysql -hlocalhost -uroot -pcallanor -e "GRANT RELOAD, PROCESS, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'replication'@'192.168.56.120' IDENTIFIED BY 'Password123+';"

# Run the following command to test the configuration. Use the private IP address of the opposing Linode:
# mysql -u replication -p -h 192.168.56.120 -P 3306

# Execute this steps manually for now
# mysql -hlocalhost -uroot -pcallanor
# STOP SLAVE;
# CHANGE MASTER TO master_host='192.168.56.120', master_port=3306, master_user='replication', master_password='Password123+', master_log_file='mysql-bin.000006', master_log_pos=462;
# START SLAVE;

