from pymongo import MongoClient
import datetime
import pymongo

client = MongoClient()

client = MongoClient('mongodb://mongodb_server:27017')

db = client['test']

posts = db.posts
post_data = {
    'title': 'Python and MongoDB',
    'content': 'PyMongo is fun, you guys',
    'author': 'Scott'
}
result = posts.insert_one(post_data)
print('One post: {0}'.format(result.inserted_id))


post_2 = {
    'title': 'Virtual Environments',
    'content': 'Use virtual environments, you guys',
    'author': 'Scott'
}
post_3 = {
    'title': 'Learning Python',
    'content': 'Learn Python, it is easy',
    'author': 'Bill'
}
new_result = posts.insert_many([post_2, post_3])
print('Multiple posts: {0}'.format(new_result.inserted_ids))

bills_post = posts.find_one({'author': 'Bill'})
print(bills_post)


print("View all documents: ")
cursor = posts.find()
for document in cursor:
    print(document)

print("Remove All Documents: ")
result = posts.delete_many({})
print("To see the number of documents deleted: ", result.deleted_count)
