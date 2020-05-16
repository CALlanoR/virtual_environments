import json
import datetime
import http.client
from time import time

########################################################################################################################
##################################################### ENVIRONMENTS #####################################################
########################################################################################################################

# connection to publications api service
# conn = http.client.HTTPConnection("localhost:5015")
conn = http.client.HTTPConnection("localhost:8282")


########################################################################################################################
######################################################## LOGIN #########################################################
########################################################################################################################

def login():
    # connection to users api service
    conn_login = http.client.HTTPConnection("localhost:8181")
    headers_default = {'Content-type': 'application/json'}

    login_post = {
        'username': 'blue',
        'password': '123456'
    }
    json_data_post = json.dumps(login_post)
    conn_login.request("POST", "/users/login", json_data_post, headers={'Content-type': 'application/json'})

    res = conn_login.getresponse()
    data = res.read()

    data_json = json.loads(data.decode("utf-8"))
    # print(data_json)
    jwt_token = data_json['token']

    headers = {
        'Content-type': 'application/json',
        'authorization': jwt_token
    }

    return headers

###############
#### LOGIN ####
###############
headers = login()
# print(headers)
# headers={'Content-type': 'application/json'}

login_post = {
    'user_id': 1,
    'description': 'El Dr. Rashid Buttar acusa a Bill Gates y Anthony Faucci la máxima autoridad en el manejo de la pandemia del coronavirus en EE.UU., de crear SARS-COV2 y de intentar vacunar en masa a la población para diezmarla y controlarla'
}
json_data_post = json.dumps(login_post)
conn.request("POST", "/publications", json_data_post, headers=headers)

# conn.request("GET", "/ping", headers={'Content-type': 'application/json'})

start = datetime.datetime.now()
res = conn.getresponse()
end = datetime.datetime.now()

data = res.read()

elapsed = end - start

print(data.decode("utf-8"))
print("\"" + str(res.status) + "\"")
print("\"" + str(res.reason) + "\"")
print("\"elapsed seconds: " + str(elapsed) + "\"")

