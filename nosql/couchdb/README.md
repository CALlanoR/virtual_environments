Links
https://hub.docker.com/_/couchdb/
https://pythonhosted.org/CouchDB/
https://pypi.python.org/pypi/CouchDB
https://pythonhosted.org/CouchDB/client.html

1. Create a container (the server)
sudo docker run --name couchdb_server -p 5984:5984 -d couchdb

This image includes EXPOSE 5984 (the CouchDB port), so standard container linking will make it automatically available to the linked containers.

Verify in your local machine: http://localhost:5984


2. Create another container (the client)
sudo docker run -itd --link couchdb_server --name couchdb_client ubuntu:14.04 /bin/bash

2.0 sudo docker exec -ti couchdb_client bash

2.1 Install curl to verify the connection with the couchdb_server
apt-get update
apt-get install -y curl vim nano

Optional:
curl http://couchdb_server:5984

2.2 Install pip to download the couchdb python library
curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
python3 get-pip.py

pip install couchdb

2.3 Copy couchdb_test.py and run it.
2.4 API (http://docs.couchdb.org/en/2.0.0/api/) Try this:
curl http://couchdb_server:5984/_all_dbs
curl http://couchdb_server:5984/test
curl http://couchdb_server:5984/test/_all_docs
curl http://couchdb_server:5984/test/lisa
curl http://couchdb_server:5984/test/lisa?revs_info=true
curl http://couchdb_server:5984/test/e58ee8658290e858b425447cea0041dd?revs_info=true
Retrieve previous revision
curl http://couchdb_server:5984/test/e58ee8658290e858b425447cea0041dd?rev=1-ef4ccb2bd0f0ed2248e189f6f6ac309d
