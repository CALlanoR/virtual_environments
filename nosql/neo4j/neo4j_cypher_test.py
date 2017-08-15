from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client

db = GraphDatabase("http://localhost:7474", username="neo4j", password="callanor")
q = 'MATCH (u:User)-[r:likes]->(m:Beer) WHERE u.name="Marco" RETURN u, type(r), m'
# "db" as defined above
results = db.query(q, returns=(client.Node, str, client.Node))
for r in results:
    print("(%s)-[%s]->(%s)" % (r[0]["name"], r[1], r[2]["name"]))
# The output:
# (Marco)-[likes]->(Punk IPA)
# (Marco)-[likes]->(Hoegaarden Rosee)


'''The query language for Neo4j is called Cypher.
It allows to describe patterns in graphs, in a declarative fashion, i.e. just like SQL,
you describe what you want, rather then how to retrieve it.
Cypher uses some sort of ASCII-art to describe nodes, relationships and their direction.'''
