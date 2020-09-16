import json
import datetime
import http.client
from time import time

########################################################################################################################
##################################################### ENVIRONMENTS #####################################################
########################################################################################################################

#local
conn = http.client.HTTPConnection("localhost:5000")

#container
# conn = http.client.HTTPConnection("localhost:5000")

########################################################################################################################
######################################################## USERS #########################################################
########################################################################################################################


headers = {
    'Content-type': 'application/json'
}

#Create person

# create_person_post = {
#     'id': 3,
#     'name': 'Carlos',
#     'email': 'carlos@gmail.com',
#     'login': 'llano',
#     'password': '123456'
# }
# json_data_post = json.dumps(create_person_post)
# conn.request("POST", "/persons/", json_data_post, headers=headers)

#Friends of a person

#conn.request("GET", "/persons/1/friends", headers=headers)

#Friends of the friends of a person

#conn.request("GET", "/persons/0/mayYouKnow", headers=headers)

#Add a new relationship

conn.request("POST", "/persons/person1/3/person2/4", headers=headers)

#Delete a relationship

# conn.request("POST", "/persons/delete/person1/3/person2/4", headers=headers)



start = datetime.datetime.now()
res = conn.getresponse()
end = datetime.datetime.now()

data = res.read()

elapsed = end - start

print(data.decode("utf-8"))
print("\"" + str(res.status) + "\"")
print("\"" + str(res.reason) + "\"")
print("\"elapsed seconds: " + str(elapsed) + "\"")

