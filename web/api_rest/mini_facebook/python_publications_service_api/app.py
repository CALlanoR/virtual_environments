from flask import Flask
from flask_cors import CORS, cross_origin
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)

### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Python-Flask-REST-PublicationsService"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT,
                       url_prefix=SWAGGER_URL)