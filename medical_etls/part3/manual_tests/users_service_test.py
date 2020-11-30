import json
import datetime
import http.client
from time import time

########################################################################################################################
##################################################### ENVIRONMENTS #####################################################
########################################################################################################################

# local
conn = http.client.HTTPConnection("localhost:8080")

# vagrant
# conn = http.client.HTTPConnection("192.168.56.119:8080")

# container
# conn = http.client.HTTPConnection("localhost:5000")

########################################################################################################################
######################################################## LOGIN #########################################################
########################################################################################################################

# login_post = {
#     'username': 'blue',
#     'password': '123456'
# }
# json_data_post = json.dumps(login_post)
# conn.request("POST", "/login", json_data_post, headers={'Content-type': 'application/json'})


########################################################################################################################
######################################################## USERS #########################################################
########################################################################################################################

#################################################
########## Encontrar todos los usuarios #########
#################################################

# headers = {
#     'Content-type': 'application/json',
#     'authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJibHVlIiwiaWRlbnRpdHkiOiJibHVlIiwiYXV0aG9yaXRpZXMiOlsiUk9MRV9VU0VSIl0sImlhdCI6MTYwNjc2NDgwOSwiZXhwIjoxNjA2NzY1NDA5fQ.bMLVhc-RL13fw8WyTa9cW3aTgU2pMzKulX8pMyEn1iCNzeWn61bc81OB9R78WvL4tLnnVjIDyA0oJBIWPEPxeQ'
# }
# conn.request("GET", "/users/", headers=headers)




#################################################
########## Encontrar un usuario por id ##########
#################################################

# headers = {
#     'Content-type': 'application/json',
#     'authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJibHVlIiwiaWRlbnRpdHkiOiJibHVlIiwiYXV0aG9yaXRpZXMiOlsiUk9MRV9VU0VSIl0sImlhdCI6MTYwNjI1MDM4MywiZXhwIjoxNjA2MjUwOTgzfQ.z7P1qmqH0PWsC4i81NawX1Tp5p8M8Bl39FPoVCTeiVvxPorzysOq2Ql7I_ENyPjwqhdSxHW0Wrua6SEp9_qClA'
# }
# conn.request("GET", "/users/1", headers=headers)


# headers = {
#     'Content-type': 'application/json',
#     'authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJibHVlIiwiaWRlbnRpdHkiOiJibHVlIiwiYXV0aG9yaXRpZXMiOlsiUk9MRV9VU0VSIl0sImlhdCI6MTYwNjI3MjQ1MywiZXhwIjoxNjA2MjczMDUzfQ.Su_POgVhOwQtyW3TXvRLwzK6aD278naT4pEXzeJRllkJzz2QfPXpKEmeRHHIo5U-t-zCB97f0GFSpvVM2GGZdA'
# }
# conn.request("DELETE", "/users/3", headers=headers)


############################################
########## Crear un nuevo usuario ##########
############################################
# headers = {
#     'Content-type': 'application/json',
#     'authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJibHVlIiwiaWRlbnRpdHkiOiJibHVlIiwiYXV0aG9yaXRpZXMiOlsiUk9MRV9VU0VSIl0sImlhdCI6MTYwNjI1MDM4MywiZXhwIjoxNjA2MjUwOTgzfQ.z7P1qmqH0PWsC4i81NawX1Tp5p8M8Bl39FPoVCTeiVvxPorzysOq2Ql7I_ENyPjwqhdSxHW0Wrua6SEp9_qClA'
# }

# user_post = {
    # 'email': 'mrwhite@gmail.com',
    # 'username': 'white',
    # 'password': 'qwerty',
    # 'name': 'James White'
# }
# json_data_post = json.dumps(user_post)
# conn.request("POST", "/users", json_data_post, headers=headers)

############################################


start = datetime.datetime.now()
res = conn.getresponse()
end = datetime.datetime.now()

data = res.read()

elapsed = end - start

print(data.decode("utf-8"))
print("\"" + str(res.status) + "\"")
print("\"" + str(res.reason) + "\"")
print("\"elapsed seconds: " + str(elapsed) + "\"")

