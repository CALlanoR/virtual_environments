from neo4j import GraphDatabase, basic_auth

def setup_neo4j_driver(host, port, login, password):
    try:
        uri = f"bolt://{host}:{port}"
        driver = GraphDatabase.driver(uri,
                                      auth=basic_auth(login, password),
                                      encrypted=False)

        return driver
    except:
        pass

driver = setup_neo4j_driver("MyNeo4JServiceDB", "7687", "neo4j", "password")
# print(driver)

with driver.session() as session:
    # delete all nodes
    session.run("MATCH (n) DETACH DELETE n")

    # delete all relations
    session.run("MATCH ()-[r]-() DELETE r")
    
    juan = session.run("CREATE (juan:Person {name:$name, age:43}) "
                       "RETURN id(juan)", name="Juan").single().value()
    erica = session.run("CREATE (erica:Person {name:$name, age:25}) "
                       "RETURN id(erica)", name="Erica").single().value()
    tomas = session.run("CREATE (tomas:Person {name:$name, age:32}) "
                    "RETURN id(tomas)", name="Tomas").single().value()
    valentina = session.run("CREATE (valentina:Person {name:$name, age:39}) "
                            "RETURN id(valentina)", name="Valentina").single().value()
    laura = session.run("CREATE (laura:Person {name:$name, age:25}) "
                       "RETURN id(laura)", name="Laura").single().value()
    jose = session.run("CREATE (jose:Person {name:$name, age:32}) "
                    "RETURN id(jose)", name="Jose").single().value()

    session.run("""Match (juan:Person{name:'Juan'}) 
                   Match (tomas:Person{name:'Tomas'})
                   Match (jose:Person{name:'Jose'})
                   Create (juan)-[:FRIEND]->(tomas)-[:FRIEND]->(jose) """)

    session.run("""Match (tomas:Person{name:'Tomas'})
                   Match (valentina:Person{name:'Valentina'})
                   Create (tomas)-[:FRIEND]->(valentina)""")

    session.run("""Match (erica:Person{name:'Erica'})
                   Match (laura:Person{name:'Laura'})
                   Create (laura)-[:FRIEND]->(erica)-[:FRIEND]->(laura) """)

    session.run("""Match (juan:Person{name:'Juan'}) 
                   Match (erica:Person{name:'Erica'})
                   Match (laura:Person{name:'Laura'})
                   Create (juan)-[:FRIEND]->(erica)-[:FRIEND]->(laura) """)

    result = session.run("MATCH (n:Person) RETURN n.name as name, n.age as age LIMIT 25").data()
    print("----------------------------")
    print("Todos las personas")
    for person in result:
        name = person['name']
        age = person['age']
        print(f"name: {name} - age: {age}")

    result = session.run("MATCH (tomas {name: 'Tomas'})-[:FRIEND]->(fof) RETURN fof.age as age, fof.name as name").data()
    print("----------------------------")
    print("Amigos de Tomas:")
    for person in result:
        name = person['name']
        age = person['age']
        print(f"name: {name} - age: {age}")

    result = session.run("MATCH (juan {name: 'Juan'})-[:FRIEND]->(fof) RETURN fof.age as age, fof.name as name").data()
    print("----------------------------")
    print("Amigos de Juan:")
    for person in result:
        name = person['name']
        age = person['age']
        print(f"name: {name} - age: {age}")

    result = session.run("MATCH (fof)<-[:FRIEND]-(laura {name: 'Laura'}) RETURN fof.age as age, fof.name as name").data()
    print("----------------------------")
    print("Amigos de Laura:")
    for person in result:
        name = person['name']
        age = person['age']
        print(f"name: {name} - age: {age}")

    result = session.run("MATCH (juan {name: 'Juan'})-[:FRIEND]->()-[:FRIEND]->(fof) RETURN fof.age as age, fof.name as name").data()
    print("----------------------------")
    print("Quizas conozcas:")
    for person in result:
        name = person['name']
        age = person['age']
        print(f"name: {name} - age: {age}")

driver.close()