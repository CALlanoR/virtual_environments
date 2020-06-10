from neo4j import GraphDatabase
from db_config import driver

class PersonsRepository(object):

    def add_person(self, id, name, email, login, password):
        with driver.session() as session:
            result = session.run("CREATE (n:Person{id:$_id, name:$_name, email:$_email, login:$_login, password:$_password})",
                                 _id=id, _name=name, _email=email, _login=login, _password=password).value()
            return result

    def get_all_persons(self):
        with driver.session() as session:
            result = session.run("MATCH (n:Person) RETURN n.name as name, n.age as age LIMIT 25").data()
            return result

    def get_person_by_name(self, name):
        with driver.session() as session:
            result = session.run("MATCH (n:Person{name:'" +name+ "'}) RETURN n.name as name, n.age as age").data()
            return result

    def get_friends(self, personId):
        with driver.session() as session:
            result = session.run("MATCH (n:Person{id:$id})-[:FRIEND]->(fof) RETURN fof.name as name", id=int(personId)).data()
            return result

    def get_friends_from_my_friends(self, personId):
        with driver.session() as session:
            result = session.run("MATCH (n:Person{id:$id})-[:FRIEND]->(myFriends)-[:FRIEND]->(othersFriends) RETURN othersFriends.name as name", id=int(personId)).data()
            return result

    def add_new_relationship(self, personId1, personId2):
        with driver.session() as session:
            result = session.run("MATCH (n:Person{id:$id1})\n"
                                 "MATCH (m:Person{id:$id2})\n"
                                 "MERGE (n)-[:FRIEND]->(m)-[:FRIEND]->(n)", id1=int(personId1), id2=int(personId2)).data()
            return result
    
    def delete_relationship(self, personId1, personId2):
        with driver.session() as session:
            result = session.run("MATCH (n:Person{id:$id1})-[r1:FRIEND]->(m:Person{id:$id2})-[r2:FRIEND]->(n)\n"
                                 "DELETE r1, r2", id1=int(personId1), id2=int(personId2))
        return result