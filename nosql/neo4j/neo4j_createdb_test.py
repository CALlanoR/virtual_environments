from neo4jrestclient.client import GraphDatabase

db = GraphDatabase("http://localhost:7474", username="neo4j", password="callanor")

'''In this example, users and things will be nodes in our database.
Each node can be associated with labels, used to describe the type of node.
The following code will create two nodes labelled as User and two nodes labelled as Beer'''

# Create some nodes with labels
user = db.labels.create("User")
user_marco = db.nodes.create(name="Marco")
user.add(user_marco)
user_daniela = db.nodes.create(name="Daniela")
user.add(user_daniela)

beer = db.labels.create("Beer")
corona_beer = db.nodes.create(name="Corona")
club_beer = db.nodes.create(name="Club Colombia")
# You can associate a label with many nodes in one go
beer.add(corona_beer, club_beer)

'''The second step is all about connecting the dots, which in graph DB terminology means
creating the relationships. '''

# User-likes->Beer relationships
user_marco.relationships.create("likes", corona_beer)
user_marco.relationships.create("likes", club_beer)
user_daniela.relationships.create("likes", corona_beer)
# Bi-directional relationship?
user_marco.relationships.create("friends", user_daniela)


'''The query language for Neo4j is called Cypher.
It allows to describe patterns in graphs, in a declarative fashion, i.e. just like SQL,
you describe what you want, rather then how to retrieve it.
Cypher uses some sort of ASCII-art to describe nodes, relationships and their direction.'''
