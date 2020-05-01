from repositories.UsersRepository import UsersRepository
from app import app


class UsersService(object):
    def __init__(self):
        self.users_repository = UsersRepository()

    def login(self,
              username,
              password):
        return self.users_repository.login(username,
                                           password)

    def get_user_by_id(self, id):
        return self.users_repository.get_user_by_id(id)

    def users_count(self):
        response = self.users_repository.count()
        return int(response['count'])