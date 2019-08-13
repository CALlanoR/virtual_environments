#!/usr/bin/env bash
yum update
yum install -y wget
yum install -y epel-release

curl -L https://www.opscode.com/chef/install.sh | bash