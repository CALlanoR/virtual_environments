from flask import Blueprint, request
from services.PersonsService import PersonsService
from flask import jsonify

persons_api = Blueprint('persons_api', __name__)

persons_service = PersonsService()

@persons_api.route('/persons/', methods=['POST'])
def add_person():
    try:
        _json = request.json
        _id = _json['id']
        _name = _json['name']
        _email = _json['email']
        _login = _json['login']
        _password = _json['password']
        # validate the received values
        if _name and request.method == 'POST':
            persons_service.add_person(int(_id), _name, _email, _login, _password)
            return 'person with id: ' +_id +' inserted'
        else:
            return not_found()
    except Exception as e:
        print(e)

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

@persons_api.route('/persons/<int:personId>/friends', methods=['GET'])
def get_friends(personId):
    try:
        row = persons_service.get_friends(personId)
        resp = jsonify(row)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)

@persons_api.route('/persons/<string:name>/byName', methods=['GET'])
def get_person_by_name(name):
    try:
        row = persons_service.get_person_by_name(name)
        resp = jsonify(row)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)

@persons_api.route('/persons/<int:personId>/mayYouKnow', methods=['GET'])
def get_friends_from_my_friends(personId):
    try:
        row = persons_service.get_friends_from_my_friends(personId)
        resp = jsonify(row)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)

@persons_api.route('/persons/person1/<int:personId1>/person2/<int:personId2>', methods=['POST'])
def add_new_relationship(personId1, personId2):
    try:
        if personId1 and personId2:
            persons_service.add_new_relationship(personId1, personId2)
            return str(personId1)+' and '+str(personId2)+' are friends now.'
        else:
            return not_found()
    except Exception as e:
        print(e)

@persons_api.route('/persons/delete/person1/<int:personId1>/person2/<int:personId2>', methods=['POST'])
def delete_relationship(personId1, personId2):
    try:
        if personId1 and personId2:
            persons_service.delete_relationship(personId1, personId2)
            return str(personId1)+' and '+str(personId2)+' are not longer friends.'
        else:
            return not_found()
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