from app import app
from flask import jsonify, request
from controllers.UsersApi import users_api

# Register each api here
app.register_blueprint(users_api)

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

if __name__ == "__main__":
    app.run(debug=True,
            host='0.0.0.0',
            port=5010)