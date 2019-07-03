import json
import datetime
import http.client
from time import time
from urllib.parse import quote
from urllib.parse import unquote # Only to remember

########################################################################################################################
##################################################### ENVIRONMENTS #####################################################
########################################################################################################################

#local
conn = http.client.HTTPConnection("localhost:9090")

########################################################################################################################
######################################################## USERS #########################################################
########################################################################################################################

conn.request("GET", "/mini-amazon/api/users", headers={'Content-type': 'application/json'})
#conn.request("GET", "/mini-amazon/api/users/mrblack4", headers={'Content-type': 'application/json'})

# create_user_post = {
#     "username": "mryellow",
#     "status":"active",
#     "stars": 3.2
# }
# json_data_post = json.dumps(create_user_post)
# conn.request("POST", "/mini-amazon/api/users", json_data_post, headers={'Content-type': 'application/json'})

#conn.request("DELETE", "/mini-amazon/api/users/mrgreen", headers={'Content-type': 'application/json'})

start = datetime.datetime.now()
res = conn.getresponse()
end = datetime.datetime.now()

data = res.read()

elapsed = end - start

print(data.decode("utf-8"))
print("\"" + str(res.status) + "\"")
print("\"" + str(res.reason) + "\"")
print("\"elapsed seconds: " + str(elapsed) + "\"")

