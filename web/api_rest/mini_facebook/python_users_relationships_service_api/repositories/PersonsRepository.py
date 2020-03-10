from neo4j import GraphDatabase
from db_config import driver

class PersonsRepository(object):

    def add_person(self, name):
        print("To Do")

    def get_all_persons(self):
        with driver.session() as session:
            result = session.run("MATCH (n:Person) RETURN n.name as name LIMIT 25").data()
            return result

    def get_person_by_name(self, name):
        print("To Do")

    def get_friends(self, name):
        print("To Do")

    def get_friends_from_my_friends(self, name):
        print("To Do")

    def add_new_relationship(self, personId1, personId2):
        