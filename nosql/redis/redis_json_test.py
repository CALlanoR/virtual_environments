from rejson import Client, Path

rj = Client(host='localhost',
            port=6379,
            decode_responses=True)

employee = {
    'name': "Juan", 
    'Age': '5', 
    'address': {
        'location': "COL"
    }
}
rj.jsonset('employee', Path.rootPath(), employee)
response1 = rj.jsonget('employee', Path('.address.location'))
print(response1)
response2 = rj.jsonget('employee', Path.rootPath())
print(response2)