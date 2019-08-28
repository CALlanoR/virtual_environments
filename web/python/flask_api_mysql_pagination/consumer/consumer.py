import json
import datetime
import http.client
from time import time

########################################################################################################################
##################################################### ENVIRONMENTS #####################################################
########################################################################################################################

#local
conn = http.client.HTTPConnection("localhost:5008")

########################################################################################################################
######################################################## USERS #########################################################
########################################################################################################################

#conn.request("GET", "/rol?page=0", headers={'Content-type': 'application/json'})

conn.request("GET", "/rol?page=1&name=%director%", headers={'Content-type': 'application/json'})


#conn.request("GET", "/rol/1", headers={'Content-type': 'application/json'})

# create_rol_post = {
#     'name': 'coWriter1'
# }
# json_data_post = json.dumps(create_rol_post)
# conn.request("POST", "/rol", json_data_post, headers={'Content-type': 'application/json'})

# create_rol_post = {
#     'name': 'coWriter8'
# }
# json_data_post = json.dumps(create_rol_post)
# conn.request("PUT", "/rol/14", json_data_post, headers={'Content-type': 'application/json'})

#conn.request("DELETE", "/rol/14", headers={'Content-type': 'application/json'})


start = datetime.datetime.now()
res = conn.getresponse()
end = datetime.datetime.now()

data = res.read()

elapsed = end - start

print(data.decode("utf-8"))
print("\"" + str(res.status) + "\"")
print("\"" + str(res.reason) + "\"")
print("\"elapsed seconds: " + str(elapsed) + "\"")

