from repositories.PersonsRepository import PersonsRepository

class PersonsService(object):
    def __init__(self):
        self.persons_repository = PersonsRepository()

    # def add_person(self, name):
    #     return self.persons_repository.add_person(name)

    def get_all_persons(self):
        return self.persons_repository.get_all_persons()

    def add_new_relationship(self, personId1, personId2):
        return self.persons_repository.add_new_relationship(personId1, personId2)