from app import app
from flask_jwt_extended import JWTManager

# Setup rabbitmq
app.config['rabbitmq_user'] = 'rabbitmq'
app.config['rabbitmq_password'] = 'rabbitmq'
app.config['rabbitmq_host'] = 'localhost'
app.config['rabbitmq_port'] = 5672
app.config['rabbitmq_exchange'] = 'new_publication_event'

app.config['mongodb_url'] = 'mongodb://localhost:27017'
app.config['mongodb_username'] = 'root'
app.config['mongodb_password'] = 'example'

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'mySecretKey'  # Change this!
app.config['JWT_ALGORITHM'] = 'HS512'
app.config['JWT_EXP_DELTA_SECONDS'] = 60
app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']
jwt = JWTManager(app)