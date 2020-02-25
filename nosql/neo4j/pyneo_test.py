from py2neo import Node, Relationship, Graph

def setup_neo4j_driver(host, port, password):
    try:
        cnx = f"http://{host}:{port}"
        print(cnx)
        graph = Graph(cnx,
                      username='neo4j',
                      password=password)
        return graph
    except:
        pass

graph = setup_neo4j_driver("127.0.0.1", "7474", "neo4j")

juan = Node('Person', name='Juan', age=21, location='Colombia')
jaime = Node('Person', name='Jaime', age=22, location='Costa Rica')
andres = Node('Person', name='Andres', age=21, location='Chile')
r1_juan_jaime = Relationship(juan, 'FRIEND', jaime)
r2_jaime_andres = Relationship(jaime, 'FRIEND', andres)
graph.create(juan)
graph.create(jaime)
graph.create(andres)
graph.create(r1_juan_jaime)
graph.create(r2_jaime_andres)

results = graph.cypher.execute("MATCH (juan {name: 'Juan'})-[:FRIEND]->()-[:FRIEND]->(fof) RETURN juan.name, fof.name")

print(results)
