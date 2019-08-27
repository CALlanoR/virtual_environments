from app import app
from flaskext.mysql import MySQL

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'dev'
app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
app.config['MYSQL_DATABASE_DB'] = 'MyDBMovies'
app.config['MYSQL_DATABASE_HOST'] = '172.21.0.2'   #'172.20.0.2' #'MySQLMoviesDB'
mysql.init_app(app)