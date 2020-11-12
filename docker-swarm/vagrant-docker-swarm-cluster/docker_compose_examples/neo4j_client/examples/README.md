https://hub.docker.com/_/neo4j/
https://marcobonzanini.com/2015/04/06/getting-started-with-neo4j-and-python/

1. Create a server
sudo docker run --name neo4j -p 7474:7474 -p 7687:7687 --volume=$HOME/neo4j/data:/data -d neo4j
sudo docker run --name neo4j -p 7474:7474 -p 7687:7687 -d neo4j

2. Verify the database in your localhost: http://localhost:7474/
  Note: neo4j is the current password, change it! and remember it!

3. In your localmachine install:
Python3.7
https://linuxize.com/post/how-to-install-python-3-7-on-ubuntu-18-04/

Neo4j python driver
python3.7 -m pip install neo4j 

https://neo4j.com/docs/api/python-driver/current/
https://medium.com/elements/diving-into-graphql-and-neo4j-with-python-244ec39ddd94
https://github.com/neo4j/neo4j-python-driver

4. Open another terminal and execute the code neo4j_test.py NOTE: change the password!

5. View in http://localhost:7474/  Database Information click in * (asterisk)
The Neo4j Browser available at http://localhost:7474/ provides a nice way to query the DB and visualise the results, both as a list of record and in a visual form.

6. Execute neo4j_test.py
