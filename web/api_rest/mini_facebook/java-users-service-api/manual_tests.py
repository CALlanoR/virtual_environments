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
######################################################## LOGIN #########################################################
########################################################################################################################


def login():
    headers_default = {'Content-type': 'application/json'}

    conn.request("POST", "/login?username=blue&password=123456", headers=headers_default)

    res = conn.getresponse()
    data = res.read()

    data_json = json.loads(data.decode("utf-8"))
    print(data_json)
    if 'token' in data_json:
        jwt_token = data_json['token']
    else:
        print("Token not found")
        exit(0)

    headers = {
        'Content-type': 'application/json',
        'authorization': jwt_token
    }

    return headers

headers = login()

conn.request("GET", "/users", headers=headers)
#conn.request("POST", "/users?name=MrRed&email=mrred@gmail.com", headers={'Content-type': 'application/json'})

start = datetime.datetime.now()
res = conn.getresponse()
end = datetime.datetime.now()

data = res.read()

elapsed = end - start

print(data.decode("utf-8"))
print("\"" + str(res.status) + "\"")
print("\"" + str(res.reason) + "\"")
print("\"elapsed seconds: " + str(elapsed) + "\"")

