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

# Install jppf node
wget -c https://sourceforge.net/projects/jppf-project/files/jppf-project/jppf%205.2.1/JPPF-5.2.1-node.zip
unzip JPPF-5.2.1-node.zip
mkdir -p /opt/jppfnode/
rsync -r JPPF-5.2.1-node /opt/jppfnode/
chmod +x /opt/jppfnode/JPPF-5.2.1-node/startNode.sh

# Configuring node to run CustomLoadBalancer example
wget -c https://sourceforge.net/projects/jppf-project/files/jppf-project/jppf%205.2.1/JPPF-5.2.1-samples-pack.zip
unzip JPPF-5.2.1-samples-pack
cp JPPF-5.2.1-samples-pack/CustomLoadBalancer/config/node2/jppf-node.properties /opt/jppfnode/JPPF-5.2.1-node/config

# Start node
cd /opt/jppfnode/JPPF-5.2.1-node/
sh /opt/jppfnode/JPPF-5.2.1-node/startNode.sh &