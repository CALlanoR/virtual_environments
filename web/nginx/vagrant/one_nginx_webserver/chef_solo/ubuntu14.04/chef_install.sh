#!/usr/bin/env bash
apt-get update
apt-get install -y curl

curl -L https://www.opscode.com/chef/install.sh | bash