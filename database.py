#-----------------------------------------------------------------------
# pair.py
# Author: Vikash and Chris 
# Modularizes Database connection/execution/disconnection protocol
#-----------------------------------------------------------------------
import os
import MySQLdb
from sys import argv, stderr, exit

# from flaskext.mysql import MySQL
# import yaml

# app = Flask(__name__, template_folder='.')
# Self contained DB class to use in any function that must connect
# to MySQL server
class Database():
    def __init__(self):
        # if not os.path.isfile(DB_NAME):
        #     raise Exception('Database connection failed')
        # self._dbname = DB_NAME
        try:
            # db = yaml.load(open(self._dbname))
            # commented out local db details information
            # self._args = ['localhost', 'TigerPair_dev', 'cos333', 'profiledb']
            # Experimental remote db details
            self._args = ['barkachi.mycpanel.princeton.edu', 3306, 'barkachi', 'Lenibac!7952', 'barkachi_site_database']
        except Exception as e:
            raise Exception('Configuration failed:', e)
    # Initialize Connection
    def connect(self):
        try:
            args = self._args
            self._connection = MySQLdb.connect(host=args[0], port=args[1], user=args[2], passwd=args[3], db=args[4])
        except Exception as e:
            raise Exception('Connection failed:', e)
    # Disconnect (it is client's responsibility to close connection)
    def disconnect(self):
        self._connection.close()
    # Initialize cursor commit, then execute given 
    # query string that is a "GET" call
    # meaning client is requesting values from db 
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
    # Initialize cursor commit, then execute given 
    # query string with input params 
    # that is a "SET" call
    # meaning client is updating values in the DB
    def execute_set(self, query_string, params):
        try:
            cursor = self._connection.cursor()
            cursor.execute(query_string, params)
            self._connection.commit()
            cursor.close()
        except:
            self._connection.rollback()