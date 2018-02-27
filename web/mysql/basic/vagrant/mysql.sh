# Download and Install the Latest Updates for the OS
apt-get update && apt-get upgrade -y

# Set the Server Timezone to CST
echo "America/Chicago" > /etc/timezone
dpkg-reconfigure -f noninteractive tzdata

# Enable Ubuntu Firewall and allow SSH & MySQL Ports
ufw enable
ufw allow 22
ufw allow 3306

# Install essential packages
apt-get -y install zsh htop

echo "Installing MySQL 5.7 now..."

LOGFILE=/tmp/install_log.txt

echo "mysql-server-5.7 mysql-server/root_password password root" | sudo debconf-set-selections
echo "mysql-server-5.7 mysql-server/root_password_again password root" | sudo debconf-set-selections
apt-get -y install mysql-server-5.7 mysql-client >> $LOGFILE 2>&1