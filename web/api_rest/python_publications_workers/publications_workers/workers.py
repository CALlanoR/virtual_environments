from celery.utils.log import get_task_logger
from pymongo import MongoClient
from setup import app

logger = get_task_logger(__name__)

@app.task(bind=True, name='save_publication', queue='new_publications')
def save_publication(self, publication):
    logger.info(f'Saving new publication: {publication}')
    _save_publication_in_database(publication)

def _save_publication_in_database(publication):
    client = MongoClient('mongodb://localhost:27017',
                         username='root',
                         password='example')
    db = client['publicationsDB']
    result = db.publications.insert_one(publication)
    print('One post: {0}'.format(result.inserted_id))

    print("View all publications: ")
    cursor = db.publications.find()
    for publication in cursor:
        print(publication)