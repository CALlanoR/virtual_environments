from app import app
from flaskext.mysql import MySQL
from flask_jwt_extended import JWTManager

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'test'
app.config['MYSQL_DATABASE_DB'] = 'MoviesDB'
app.config['MYSQL_DATABASE_HOST'] = 'MySQLServiceDB'   #'172.20.0.2' #'MySQLServiceDB'
app.config['MYSQL_DATABASE_PORT'] = 3306
mysql.init_app(app)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'mySecretKey'  # Change this!
app.config['JWT_ALGORITHM'] = 'HS512'
jwt = JWTManager(app)