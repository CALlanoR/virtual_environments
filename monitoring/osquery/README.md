Documentation
=============
https://osquery.io/
https://github.com/osquery/osquery-python
https://github.com/facebook/osquery/tree/master/docs/wiki
https://www.proxyrack.com/how-to-install-and-use-osquery-for-monitoring-and-system-security-on-ubuntu-16-04/
https://github.com/sidorares/osquery-node

1. Create image with osquery installed
sudo docker build -t osquery_image .

2. Verify images
sudo docker images

3. Create server container
sudo docker run -di --name=osquery01 osquery_image

4. Verify ip address of each container
sudo docker ps -a
sudo docker exec -it osquery01 bash

5. /etc/init.d/rsyslog restart
   /etc/init.d/osqueryd restart

6. cd /home/workdir
7. nodejs execute_query.js
8. python execute_query.py

