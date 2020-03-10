from flask import Blueprint
from app import app
from services.PersonsService import PersonsService
from flask import jsonify

persons_api = Blueprint('persons_api', __name__)

persons_service = PersonsService()

# To Do in Class
# @persons_api.route('/persons', methods=['POST'])
# def add_person():
#     try:
#         _json = request.json
#         _name = _json['name']
#         # validate the received values
#         if _name and request.method == 'POST':
#             persons_service.add_person(_name)
#             resp.status_code = 200
#             return resp
#         else:
#             return not_found()
#     except Exception as e:
#         print(e)

@persons_api.route('/persons', methods=['GET'])
def get_all_persons():
    try:
        app.logger.info("in /persons")
        
        rows = persons_service.get_all_persons()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)

@persons_api.route('/persons/<string:name>', methods=['GET'])
def get_person_by_name(name):
    try:
        row = persons_service.get_person_by_name(name)
        row = name
        resp = jsonify(row)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)

@persons_api.route('/persons/personId1/<int:personId1>/personId2/<int:personId2>', methods=['POST'])
def add_new_relationship(personId1, personId2):
    try:
        row = persons_service.add_new_relationship(personId1, personId2)
        resp = jsonify(row)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)

@persons_api.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp