from neo4j_connection import Neo4jConnection

conn = Neo4jConnection(uri="neo4j://localhost:7687",
                       user="neo4j",
                       pwd="callanor")

conn.query("MATCH (n) DETACH DELETE n")
conn.query("MATCH ()-[r]-() DELETE r")

query = """
    CREATE (p:Person {name:$name, age:$age})
    RETURN id(p)
"""
conn.query(query, parameters = {'name': 'Juan', 'age': 43})
conn.query(query, parameters = {'name': 'Erica', 'age': 25})
conn.query(query, parameters = {'name': 'Tomas', 'age': 32})
conn.query(query, parameters = {'name': 'Valentina', 'age': 39})
conn.query(query, parameters = {'name': 'Laura', 'age': 25})
conn.query(query, parameters = {'name': 'Jose', 'age': 32})

query = """
    Match (juan:Person{name:'Juan'}) 
    Match (tomas:Person{name:'Tomas'})
    Match (jose:Person{name:'Jose'})
    Create (juan)-[:FRIEND]->(tomas)-[:FRIEND]->(jose)
"""
conn.query(query)

query = """
    Match (tomas:Person{name:'Tomas'})
    Match (valentina:Person{name:'Valentina'})
    Create (tomas)-[:FRIEND]->(valentina)
"""
conn.query(query)

query = """
    Match (juan:Person{name:'Juan'}) 
    Match (erica:Person{name:'Erica'})
    Match (laura:Person{name:'Laura'})
    Create (juan)-[:FRIEND]->(erica)-[:FRIEND]->(laura)
"""
conn.query(query)

query_beer = """
    CREATE (b:Beer {name:$name})
    RETURN id(b)
"""
conn.query(query_beer, parameters = {'name': 'Club Colombia'})
conn.query(query_beer, parameters = {'name': 'Poker'})

query = """
    Match (juan:Person{name:'Juan'})
    Match (erica:Person{name:'Erica'})
    Match (club:Beer{name:'Club Colombia'})
    Match (poker:Beer{name:'Poker'})
    Create (juan)-[:LIKES]->(club)
    Create (erica)-[:LIKES]->(poker)
"""
conn.query(query)

query = """
    MATCH (n:Person) RETURN n.name as name, n.age as age LIMIT 25
"""
result = conn.query(query)
print("----------------------------")
print("Todos las personas")
for person in result:
    name = person['name']
    age = person['age']
    print(f"name: {name} - age: {age}")

query = """
    Match (tomas:Person{name:'Tomas'})-[:FRIEND]->(fof) RETURN fof.age as age, fof.name as name
"""
result = conn.query(query)
print("----------------------------")
print("Amigos de Tomas:")
for person in result:
    name = person['name']
    age = person['age']
    print(f"name: {name} - age: {age}")

query = """
    MATCH (juan {name: 'Juan'})-[:FRIEND]->(fof) RETURN fof.age as age, fof.name as name
"""
result = conn.query(query)
print("----------------------------")
print("Amigos de Juan:")
for person in result:
    name = person['name']
    age = person['age']
    print(f"name: {name} - age: {age}")

query = """
    MATCH (juan {name: 'Juan'})-[:FRIEND]->()-[:FRIEND]->(fof) RETURN fof.age as age, fof.name as name
"""
result = conn.query(query)
print("----------------------------")
print("Quizas conozcas:")
for person in result:
    name = person['name']
    age = person['age']
    print(f"name: {name} - age: {age}")

query = """
    MATCH (beer:Beer)
    MATCH (:Person {name: 'Juan'})-->(beer) RETURN beer.name as name
"""
result = conn.query(query)
print("----------------------------")
print("Que cerveza le gusta a Juan: {}".format(result[0]['name']))

query = """
    MATCH (person:Person)
    MATCH (beer:Beer{name:'Poker'})
    MATCH (person)-[:LIKES]->(beer) RETURN person.age as age, person.name as name
"""
result = conn.query(query)
print("----------------------------")
print("A quienes les gusta la Poker:")
for person in result:
    name = person['name']
    age = person['age']
    print(f"name: {name} - age: {age}")