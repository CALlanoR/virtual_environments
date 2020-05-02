from flask import Blueprint
from flask import jsonify, request
from flask_jwt_extended import (
    jwt_required, fresh_jwt_required, JWTManager, jwt_refresh_token_required,
    jwt_optional, create_access_token, create_refresh_token, get_jwt_identity,
    decode_token
)
from services.PublicationsService import PublicationsService
from app import app

publications_api = Blueprint('publications_api', __name__)

publications_service = PublicationsService()

@users_api.route('/publications',
                 methods = ['POST'])
def create_publication():
    try:
        app.logger.info("in /publications")
        publication_body = request.json
        if 'user_id' in publication_body and 'description' in publication_body:
            app.logger.info("user_id: " + str(publication_body['user_id']))
            result = publications_service.create_publication(publication_body)
            if result:
                resp = jsonify({'message': 'publication received'})
                resp.status_code = 201
            else:
                resp = jsonify({'message': 'publication received'})
                resp.status_code = 500
        else:
            resp = jsonify({'message': 'unknown error')
            resp.status_code = 500
        return resp
    except Exception as e:
        resp = jsonify({'message': 'unknown error'})
        resp.status_code = 500
        return resp