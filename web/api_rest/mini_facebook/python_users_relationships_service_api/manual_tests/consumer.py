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

conn.request("GET", "/persons", headers=headers)
# conn.request("GET", "/persons/Juan", headers=headers)

# create_person_post = {
#     'name': 'Erica'
# }
# json_data_post = json.dumps(create_person_post)
# conn.request("POST", "/persons", json_data_post, headers={'Content-type': 'application/json'})


start = datetime.datetime.now()
res = conn.getresponse()
end = datetime.datetime.now()

data = res.read()

elapsed = end - start

print(data.decode("utf-8"))
print("\"" + str(res.status) + "\"")
print("\"" + str(res.reason) + "\"")
print("\"elapsed seconds: " + str(elapsed) + "\"")

