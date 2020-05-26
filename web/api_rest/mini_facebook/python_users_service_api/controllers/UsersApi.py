from flask import Blueprint
from flask import jsonify, request
from flask_jwt_extended import (
    jwt_required, fresh_jwt_required, JWTManager, jwt_refresh_token_required,
    jwt_optional, create_access_token, create_refresh_token, get_jwt_identity,
    decode_token
)
from services.UsersService import UsersService
from db_config import cache_client
from app import app
import json

users_api = Blueprint('users_api', __name__)

users_service = UsersService()

@users_api.route('/users/login',
                 methods = ['POST'])
def login():
    try:
        app.logger.info("in /login")
        json = request.json
        username = json['username']
        password = json['password']
        user_id = users_service.login(username,
                                      password)
        if user_id is None:
            resp = jsonify({'message': 'incorrect username or password'})
            resp.status_code = 401
        else:
            app.logger.info("user_id: " + str(user_id['id']))
            access_token = create_access_token(identity=user_id['id'])
            resp = jsonify({'token': 'Bearer {}'.format(access_token)})
            resp.status_code = 200
        return resp
    except Exception as e:
        message = "unknown error, please contact the administrator"
        app.logger.error(message)
        resp = jsonify({'message': message})
        resp.status_code = 500

@users_api.route('/users',
                 methods = ['GET'])
@jwt_required
def get_users():
    try:
        app.logger.info("in /users")
        user_id = request.args.get('id', default = None, type = int)
        user_name = request.args.get('name', default = None, type = str)
        if user_id is not None:
            app.logger.info("getting user from cache")
            user = cache_client.get(str(user_id))
            if user != None:
                app.logger.info("already exists in cache")
                app.logger.info(user)
                resp = jsonify(json.loads(user.decode("utf-8").replace("'",'"')))
                resp.status_code = 200
            else:
                user = users_service.get_user_by_id(user_id)
                app.logger.info("user does not exist in the cache, creating it.")
                cache_client.set(str(user_id),
                                 user,
                                 expire=20)
                app.logger.info("user: " + str(user))
                if user is None:
                    resp = jsonify({'message': 'user not found'})
                    resp.status_code = 404
                else:
                    resp = jsonify(user)
                    resp.status_code = 200
        elif user_name is not None:
            # Buscar por nombre
            resp = jsonify({'message': 'not implemented'})
            resp.status_code = 200
        else:
            # Buscar todos los usuarios
            resp = jsonify({'message': 'not implemented'})
            resp.status_code = 200
        return resp
    except Exception as e:
        app.logger.error("in /users {0}".format(str(e)))
        resp = jsonify({'message': 'unknown error, please contact the administrator'})
        resp.status_code = 500

@users_api.route('/users/ping',
                 methods = ['GET'])
def ping():
    try:
        app.logger.info("in /ping")
        count = users_service.users_count()
        if count > 1:
            resp = jsonify({'message': 'pong'})
            resp.status_code = 200
        else:
            resp = jsonify({'message': 'error'})
            resp.status_code = 500
    except Exception as e:
        app.logger.error(str(e))
        resp = jsonify({'message': 'error'})
        resp.status_code = 500
    return resp