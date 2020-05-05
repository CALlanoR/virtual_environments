from pymongo import MongoClient
from app import app
import db_config

class PublicationsRepository(object):
    def __init__(self):
        self.client = MongoClient(app.config['mongodb_url'],
                                  username=app.config['mongodb_username'],
                                  password=app.config['mongodb_password'])

    def count(self):
        print("count all publications...")
        db = self.client['publicationsDB']
        return db.publications.count_documents({})
