from app import app
from flaskext.mysql import MySQL
from flask_jwt_extended import JWTManager
from pymemcache.client.hash import HashClient

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'test'
app.config['MYSQL_DATABASE_DB'] = 'UsersDB'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'   #'localhost' 'MySQLServiceDB'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_USE_POOL'] = {
    #use = 0 no pool else use pool
    'use': 1,
    # size is >=0,  0 is dynamic pool
    'size': 10,
    #pool name
    'name': 'local'
}
mysql.init_app(app)

cache_client = HashClient([('MemcachedServer1', 11211),
                           ('MemcachedServer2', 11211)])
                        #   serializer = True,
                        #   deserializer = True,
                        #   use_pooling = True)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'mySecretKey'  # Change this!
app.config['JWT_ALGORITHM'] = 'HS512'
app.config['JWT_EXP_DELTA_SECONDS'] = 60
jwt = JWTManager(app)