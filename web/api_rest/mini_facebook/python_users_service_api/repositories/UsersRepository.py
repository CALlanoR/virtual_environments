import pymysql
from db_config import mysql

class UsersRepository(object):
    def __init__(self):
        self.conn = mysql.connect()

    def login(self, username, password):
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id AS id FROM user WHERE username=%s AND password=%s", (username, password))
        row = cursor.fetchone()
        cursor.close()
        return row

    def get_user_by_id(self, id):
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT email, name, username FROM user WHERE id=%s", id)
        row = cursor.fetchone()
        cursor.close()
        return row

    def count(self):
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT count(id) as count FROM user")
        row = cursor.fetchone()
        cursor.close()
        return row