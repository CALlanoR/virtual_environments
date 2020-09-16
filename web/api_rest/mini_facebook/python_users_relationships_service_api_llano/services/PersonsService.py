from repositories.PersonsRepository import PersonsRepository

class PersonsService(object):
    def __init__(self):
        self.persons_repository = PersonsRepository()

    def add_person(self, id, name, email, login, password):
        return self.persons_repository.add_person(id, name, email, login, password)

    def get_all_persons(self):
        return self.persons_repository.get_all_persons()

    def get_person_by_name(self, name):
    	return self.persons_repository.get_person_by_name(name)

    def get_friends(self, personId):
        return self.persons_repository.get_friends(personId)
    
    def get_friends_from_my_friends(self, personId):
        return self.persons_repository.get_friends_from_my_friends(personId)

    def add_new_relationship(self, personId1, personId2):
        return self.persons_repository.add_new_relationship(personId1, personId2)
    
    def delete_relationship(self, personId1, personId2):
        return self.persons_repository.delete_relationship(personId1, personId2)