import os
import sqlite3
from sys import argv, stderr, exit
from flask_mysqldb import MySQL
from flask import Flask
import yaml

DB_NAME = "database.yaml"
app = Flask(__name__, template_folder='.')

class Database():
    def __init__(self):
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
            self._connection = MySQL(_app)
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

def selectall_query(table):
    return f'SELECT * FROM {table}'

# number of features
N = 2
def get_rankings(weight_vector):
    db = Database()
    db.connect()
    students = db.execute(selectall_query("students"), ())
    alumni = db.execute(selectall_query("alumni"), ())
    
    students_alumni = {}
    for i in range(len(students)):
        student_alumni = []
        # assuming index 0 netid, index 1 is major, index 2 is career
        for j in range(len(alumni)):
            # can easily use this form to generalize to any number of features (columns will definitely change so keep an eye on range() especially)
            score = sum(weight_vector[k] * (1 if students[i][k + 1] == alumni[j][k + 1] else 0) for k in range(len(students[i]) - 1))
            student_alumni.append((alumni[j][0], score))
        students_alumni[students[i][0]] = student_alumni

    # sort rankings
    for student in students_alumni:
        students_alumni[student].sort(key=lambda x: x[1], reverse=True)

    db.disconnect()
    return students_alumni

    if __name__ == '__main__':
        pass