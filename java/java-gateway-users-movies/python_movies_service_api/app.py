from flask import Flask
from flask_cors import CORS, cross_origin
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

app = Flask(__name__)
CORS(app)