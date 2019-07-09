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
conn = http.client.HTTPConnection("localhost:7070")

########################################################################################################################
######################################################## USERS #########################################################
########################################################################################################################

#conn.request("GET", "/users", headers={'Content-type': 'application/json'})
conn.request("POST", "/users?name=MrRed2&email=mrred2@gmail.com", headers={'Content-type': 'application/json'})

start = datetime.datetime.now()
res = conn.getresponse()
end = datetime.datetime.now()

data = res.read()

elapsed = end - start

print(data.decode("utf-8"))
print("\"" + str(res.status) + "\"")
print("\"" + str(res.reason) + "\"")
print("\"elapsed seconds: " + str(elapsed) + "\"")

