#!/usr/bin/env bash

# Install java and ant
sudo apt-get install -y python-software-properties debconf-utils
sudo add-apt-repository -y ppa:webupd8team/java
sudo apt-get update
echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | sudo debconf-set-selections
sudo apt-get install -y oracle-java8-installer ant unzip

# Configure java and ant
echo "JAVA_HOME=\"/usr/lib/jvm/java-8-oracle\"" >> /etc/environment
echo "ANT_HOME=\"/usr/share/ant\"" >> /etc/environment
echo "PATH=JAVA_HOME/bin:/ANT_HOME/bin:$PATH" >> /etc/environment

# Install jppf server
wget -c https://sourceforge.net/projects/jppf-project/files/jppf-project/jppf%205.2.1/JPPF-5.2.1-driver.zip
unzip JPPF-5.2.1-driver.zip
mkdir -p /opt/jppfserver/
rsync -r JPPF-5.2.1-driver /opt/jppfserver/
chmod +x /opt/jppfserver/JPPF-5.2.1-driver/startDriver.sh

# Configuring node to run CustomLoadBalancer example
wget -c https://sourceforge.net/projects/jppf-project/files/jppf-project/jppf%205.2.1/JPPF-5.2.1-samples-pack.zip
unzip JPPF-5.2.1-samples-pack
cd JPPF-5.2.1-samples-pack/CustomLoadBalancer/
ant jar
cp CustomLoadBalancer.jar /opt/jppfserver/JPPF-5.2.1-driver/lib
echo "CLASSPATH=/opt/jppfserver/JPPF-5.2.1-driver/lib:.:$CLASSPATH" >> /etc/environment
sed -i -e 's/jppf.load.balancing.algorithm = proportional/jppf.load.balancing.algorithm = customLoadBalancer/g' /opt/jppfserver/JPPF-5.2.1-driver/config/jppf-driver.properties

cd /opt/jppfserver/JPPF-5.2.1-driver/
sh /opt/jppfserver/JPPF-5.2.1-driver/startDriver.sh &
