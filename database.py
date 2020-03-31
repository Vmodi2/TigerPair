#-----------------------------------------------------------------------
# pair.py
# Author: Vikash Chris and Abhinaya
#-----------------------------------------------------------------------
import os
import MySQLdb
from sys import argv, stderr, exit

# from flaskext.mysql import MySQL
# import yaml

# app = Flask(__name__, template_folder='.')

class Database():
    def __init__(self):
        # if not os.path.isfile(DB_NAME):
        #     raise Exception('Database connection failed')
        # self._dbname = DB_NAME
        try:
            # db = yaml.load(open(self._dbname))
            # self._args = ['localhost', 'TigerPair_dev', 'cos333', 'profiledb']
            self._args = ['remotemysql.com', 3306, 'Nq7N0pfZz5', 'ApjTJUBWx7', 'Nq7N0pfZz5']
        except Exception as e:
            raise Exception('Configuration failed:', e)
    def connect(self):
        try:
            args = self._args
            self._connection = MySQLdb.connect(host=args[0], port=args[1], user=args[2], passwd=args[3], db=args[4])
        except Exception as e:
            raise Exception('Connection failed:', e)
    def disconnect(self):
        self._connection.close()
    def execute_get(self, query_string):
        try:
            cursor = self._connection.cursor()
            cursor.execute(query_string)
            self._connection.commit()
            result = cursor.fetchall()
            cursor.close()
            return result
        except:
            self._connection.rollback()
    def execute_set(self, query_string, params):
        try:
            cursor = self._connection.cursor()
            cursor.execute(query_string, params)
            self._connection.commit()
            cursor.close()
        except:
            self._connection.rollback()