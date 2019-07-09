from flask_swagger_ui import get_swaggerui_blueprint
from flask import Flask, request, Response
import json
import os
import socket

app = Flask(__name__)

users = [
    {
        "id": 0,
        "username": "mrblack",
        "status": "active",
        "stars": 3
    },
    {
        "id": 1,
        "username": "mrwhite",
        "status": "active",
        "stars": 4.5
    },
    {
        "id": 2,
        "username": "msblue",
        "status": "inactive",
        "stars": 1.5
    }
]


@app.route("/mini-amazon/api/users", methods=["GET"])
def get_all_users():
    return json.dumps(users)

@app.route("/mini-amazon/api/users/<username>",methods=["GET"])
def get_one_user(username):
    for user in users:
        if user['username'] == username:
            return json.dumps(user)
    return '', 204

@app.route("/mini-amazon/api/users", methods=["POST"])
def create_user():
    user_dto = request.get_json()
    next_id = len(users) + 1
    new_user = {
        "id": next_id,
        "username": user_dto['username'],
        "status" : user_dto['status'],
        "stars": user_dto["stars"]
    }
    users.append(new_user)
    return json.dumps(users)

@app.route("/mini-amazon/api/users/<username>", methods=["DELETE"])
def delete_user(username):
    print(users)
    delete_user = None
    for user in users:
        if user['username'] == username:
            print(user)
            delete_user = user
    if delete_user != None:
        users.remove(delete_user)
        print(users)
        return Response(status=200)
    else:
        return '', 204


### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Seans-Python-Flask-REST-Boilerplate"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9090)

