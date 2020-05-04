from pymongo import MongoClient

def get_all_publications():
    print("View all publications: ")
    client = MongoClient('mongodb://localhost:27017',
                         username='root',
                         password='example')
    db = client['publicationsDB']
    cursor = db.publications.find()
    for publication in cursor:
        print(publication)

get_all_publications()