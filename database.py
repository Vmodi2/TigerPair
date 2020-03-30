import os
import sqlite3
from sys import argv, stderr, exit
from flask_mysqldb import MySQL
from flask import Flask
import yaml

DB_NAME = "database.yaml"
# app = Flask(__name__, template_folder='.')

class Database():
    def __init__(self, app):
        if not os.path.isfile(DB_NAME):
            raise Exception('Database connection failed')
        self._dbname = DB_NAME
        try:
            db = yaml.load(open(self._dbname))
            app.config['MYSQL_HOST'] = db["mysql_host"]
            app.config['MYSQL_USER'] = db["mysql_user"]
            app.config['MYSQL_PASSWORD'] = db["mysql_password"]
            app.config['MYSQL_DB'] = db["mysql_db"]
            self._app = app
        except Exception as e:
            raise Exception('Configuration failed:', e)
    def connect(self):
        try:
            self._connection = MySQL(self._app)
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
        except:
            self._connection.rollback()