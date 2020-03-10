from app import app
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