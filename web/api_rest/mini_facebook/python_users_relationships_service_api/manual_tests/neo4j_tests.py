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

driver = setup_neo4j_driver("localhost", "7687", "neo4j", "password")
# print(driver)

with driver.session() as session:
    # delete all nodes
    session.run("MATCH (n) DETACH DELETE n")

    # delete all relations
    session.run("MATCH ()-[r]-() DELETE r")
    
    juan = session.run("CREATE (juan:Person {id:0, name:$name, email:$email, login:$login, password:$password}) "
                       "RETURN id(juan)", name="Juan", email="juan@email.com", login="juan123", password="12345").single().value()
    valentina = session.run("CREATE (valentina:Person {id:1, name:$name, email:$email, login:$login, password:$password}) "
                            "RETURN id(valentina)", name="Valentina", email="valentina@email.com", login="valen123", password="12345").single().value()
    jacobo = session.run("CREATE (jacobo:Person {id:2, name:$name, email:$email, login:$login, password:$password}) "
                       "RETURN id(jacobo)", name="Jacobo",email="jacobo@email.com", login="jacobo123", password="12345").single().value()
    yuritza = session.run("CREATE (yuritza:Person {id:3, name:$name, email:$email, login:$login, password:$password}) "
                    "RETURN id(yuritza)", name="Yuritza",email="yuritza@email.com", login="yuri123", password="12345").single().value()

    session.run("""Match (juan:Person{name:'Juan'}) 
                   Match (valentina:Person{name:'Valentina'})
                   Match (jacobo:Person{name:'Jacobo'})
                   Create (juan)-[:FRIEND]->(valentina)-[:FRIEND]->(jacobo)""")

    session.run("""Match (valentina:Person{name:'Valentina'})
                   Match (yuritza:Person{name:'Yuritza'})
                   Create (valentina)-[:FRIEND]->(yuritza)""")

    result = session.run("MATCH (n:Person) RETURN n.name as name, n.age as age LIMIT 25").data()
    print("Todos las personas")
    for person in result:
        name = person['name']
        age = person['age']
        print(f"name: {name} - age: {age}")

    result = session.run("MATCH (valentina {name: 'Valentina'})-[:FRIEND]->(fof) RETURN fof.age as age, fof.name as name").data()
    print("Amigos de Valentina:")
    for person in result:
        name = person['name']
        age = person['age']
        print(f"name: {name} - age: {age}")

    result = session.run("MATCH (juan {name: 'Juan'})-[:FRIEND]->(fof) RETURN fof.age as age, fof.name as name").data()
    print("Amigos de Juan:")
    for person in result:
        name = person['name']
        age = person['age']
        print(f"name: {name} - age: {age}")


driver.close()