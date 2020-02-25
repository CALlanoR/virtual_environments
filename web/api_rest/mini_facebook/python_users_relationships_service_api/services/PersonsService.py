from repositories.PersonsRepository import PersonsRepository

class PersonsService(object):
    def __init__(self):
        self.persons_repository = PersonsRepository()

    # def add_person(self, name):
    #     return self.persons_repository.add_person(name)

    def get_all_persons(self):
        return self.persons_repository.get_all_persons()