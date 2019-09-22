from app import app
from flaskext.mysql import MySQL
from flask_jwt_extended import JWTManager

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'dev'
app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
app.config['MYSQL_DATABASE_DB'] = 'MoviesDB'
app.config['MYSQL_DATABASE_HOST'] = '172.19.0.2'   #'172.20.0.2' #'MySQLMoviesDB'
app.config['MYSQL_DATABASE_PORT'] = 3306
mysql.init_app(app)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'mySecretKey'  # Change this!
app.config['JWT_ALGORITHM'] = 'HS512'
jwt = JWTManager(app)