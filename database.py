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
            self._args = ['host', 'TigerPair_dev', 'cos333', 'profiledb']
        except Exception as e:
            raise Exception('Configuration failed:', e)
    def connect(self):
        try:
            args = self._args
            self._connection = MySQLdb.connect(host=args[0], user=args[1], passwd=args[2], db=args[3])
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