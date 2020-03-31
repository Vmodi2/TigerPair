import os
from sys import argv, stderr, exit
from flask_mysqldb import MySQL
# from flask import Flask
# from flaskext.mysql import MySQL
# import yaml

# app = Flask(__name__, template_folder='.')

class Database():
    def __init__(self, app):
        # if not os.path.isfile(DB_NAME):
        #     raise Exception('Database connection failed')
        # self._dbname = DB_NAME
        try:
            # db = yaml.load(open(self._dbname))
            mysql = MySQL()
            app.config['MYSQL_DATABASE_USER'] = 'TigerPair_dev'
            app.config['MYSQL_DATABASE_PASSWORD'] = 'cos333'
            app.config['MYSQL_DATABASE_DB'] = 'profiledb'
            app.config['MYSQL_DATABASE_HOST'] = 'localhost'
            self._mysql = mysql.init_app(app)
        except Exception as e:
            raise Exception('Configuration failed:', e)
    def connect(self):
        try:
            self._connection = self._mysql.connect()
        except Exception as e:
            raise Exception('Connection failed:', e)
    def disconnect(self):
        self._connection.close()
    def execute(self, query_string, params):
        try:
            cursor = self._connection.cursor()
            cursor.execute(query_string)
            self._connection.commit()
            result = cursor.fetchall()
            cursor.close()
            return result
        except:
            self._connection.rollback()