from flask_restplus import Api, Resource, fields
from flask import Flask, request, Response
import json
import os
import socket

app = Flask(__name__)

api = Api(
    app, 
    version='1.0.0', 
    title='Users API',
    description='A simple Users API',
)

ns = api.namespace('users', description='Users operations')

user = api.model('User', {
    'id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'username': fields.String(required=True, description='The username'),
    'status': fields.String(required=True, description='The status'),
    'stars': fields.String(required=True, description='The number of stars')
})

class UserDAO(object):
    def __init__(self):
        self.counter = 0
        self.users = []

    def get(self, username):
        for user in self.users:
            if user['username'] == username:
                return user
        api.abort(404, "User {} doesn't exist".format(username))

    def create(self, data):
        new_user = data
        new_user['id'] = self.counter = self.counter + 1
        self.users.append(new_user)
        return new_user

    def update(self, username, data):
        user = self.get(username)
        user.update(data)
        return user

    def delete(self, username):
        user = self.get(username)
        self.users.remove(user)


DAO = UserDAO()
DAO.create(
    {
        "id": 0,
        "username": "mrblack",
        "status": "active",
        "stars": 3
    }
)
DAO.create(
    {
        "id": 1,
        "username": "mrwhite",
        "status": "active",
        "stars": 4.5
    }
)
DAO.create(
    {
        "id": 2,
        "username": "msblue",
        "status": "inactive",
        "stars": 1.5
    }
)

@ns.route("/")
class UsersList(Resource):
    '''Shows a list of all users, and lets you POST to add new users'''

    @ns.doc('list_users')
    @ns.marshal_list_with(user)
    def get(self):
        '''List all users'''
        return DAO.users

    @ns.doc('create_user')
    @ns.expect(user)
    @ns.marshal_with(user, code=201)
    def post(self):
        '''Create a new user'''
        return DAO.create(api.payload), 201


@ns.route('/<string:username>')
@ns.response(404, 'User not found')
@ns.param('username', 'The username identifier')
class User(Resource):
    '''Show a single user item and lets you delete them'''

    @ns.doc('get_user')
    @ns.marshal_with(user)
    def get(self, username):
        '''Fetch a given resource'''
        return DAO.get(username)

    @ns.doc('delete_user')
    @ns.response(204, 'User deleted')
    def delete(self, username):
        '''Delete a user given its username'''
        DAO.delete(username)
        return '', 204

    @ns.expect(user)
    @ns.marshal_with(user)
    def put(self, username):
        '''Update a user given its identiusernamefier'''
        return DAO.update(username, api.payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9090, debug=True)



