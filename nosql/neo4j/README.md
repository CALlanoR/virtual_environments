https://hub.docker.com/_/neo4j/
https://marcobonzanini.com/2015/04/06/getting-started-with-neo4j-and-python/

1. Create a server
sudo docker run --publish=7474:7474 --publish=7687:7687 --volume=$HOME/neo4j/data:/data neo4j

2. Verify the database in your localhost: http://localhost:7474/
  Note: neo4j is the current password, change it! and remember it!

3. In your localmachine install:
sudo pip install neo4jrestclient

4. Open another terminal and execute the code neo4j_createdb_test.py NOTE: change the password!

5. View in http://localhost:7474/  Database Information click in * (asterisk)
The Neo4j Browser available at http://localhost:7474/ provides a nice way to query the DB and visualise the results, both as a list of record and in a visual form.

6. Execute neo4j_cypher_test.py
