import couchdb
couch = couchdb.Server()

couch = couchdb.Server('http://couchdb_server:5984/')

try:
    #create a new database, or use an existing database:
    db = couch.create('test') # newly created
except:
    db = couch['test'] # existing

# After selecting a database, create a document and insert it into the db:
doc = {'type': 'Person', 'name': 'John Doe', 'passport': '1234A'}

# The save() method returns the ID and "rev" for the newly created document.
id, rev  = db.save(doc)
print("Creating a document:")
print("id: ", id)
print("rev: ", rev)
print("\n")

# Getting the document out again is easy:
document = db[id]
print("Updating a document: ")
print("Original: ", str(document))
document['name'] = 'Mary Jane'
db[id] = document
print("Updated: ", str(db[id]))

print("\n")
print ("Print all documents:")
for id in db:
    print (id)
    print ( db[id] )


print("Execute queries: ")
db['audrey'] = dict(type='Person', name='Audrey Doe')
db['lisa'] = dict(type='Person', name='Lisa Jane')
db['gotham'] = dict(type='City', name='Gotham City')
map_fun = '''function(doc) {
    if (doc.type == 'Person')
        emit(doc.name, null);
    }'''
for row in db.query(map_fun):
    print(row.key)


# Now we can clean up the test document and database we created:
db.delete(document)
couch.delete('test')
