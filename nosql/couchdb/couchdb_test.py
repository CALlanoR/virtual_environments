import couchdb

couch = couchdb.Server('http://localhost:5984/')

try:
    #create a new database, or use an existing database:
    db = couch.create('test') # newly created
except:
    db = couch['test'] # existing

# After selecting a database, create a document and insert it into the db:
doc = {'type': 'Person', 'name': 'John Doe', 'passport': '1234A', 'year': 2001}

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
    print ( db[id] )


print("Execute queries: ")
db['audrey'] = dict(type='Person', name='Audrey Doe', year=2000)
db['lisa'] = dict(type='Person', name='Lisa Jane', year=1994)
db['gotham'] = dict(type='City', name='Gotham City', year=2010)
mango = {
    'selector': {'type': 'Person'},
    'fields': ['name', 'year']
}
for row in db.find(mango):
    print(row['year'])

print("------------------------------")

mango = {
  "selector": {
    "year": {
      "$eq": 2001
    }
  },
  "fields": [
    "name", "year"
  ]
}
for row in db.find(mango):
    print(row['name'] + "-" + str(row['year']))

# To learn more about selectors
# http://docs.couchdb.org/en/master/api/database/find.html#find-selectors

# Now we can clean up the test document and database we created:
db.delete(document)
couch.delete('test')
