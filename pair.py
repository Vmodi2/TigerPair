#!/usr/bin/env python

#-----------------------------------------------------------------------
# pair.py
# Author: Tara and Abhinaya
#-----------------------------------------------------------------------

from sys import argv
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from database import Database
from flask_mysqldb import MySQL
import yaml

#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='.')

db = yaml.load(open('database.yaml'))
app.config['MYSQL_HOST'] = db["mysql_host"]
app.config['MYSQL_USER'] = db["mysql_user"]
app.config['MYSQL_PASSWORD'] = db["mysql_password"]
app.config['MYSQL_DB'] = db["mysql_db"]

mysql = MySQL(app)

#-----------------------------------------------------------------------

@app.route('../hub/student/index.html', methods=['POST'])
def student():

    argv = []

    firstname = request.form.get("firstname")
    argv.append(firstname)
    lastname = request.form.get("lastname")
    argv.append(lastname)
    email = request.form.get("email")
    argv.append(email)
    major = request.form.get("major")
    argv.append(major)
    career = request.form.get("field")
    argv.append(career)

    cursor = mysql.connection.cursor()

    query = "INSERT INTO student_table \
             VALUES ? ? ? ? "

    cursor.execute(query, (firstname, lastname, email, major, career))
    mysql.connection.commit() # try and except maybe before
    cursor.close()

#-----------------------------------------------------------------------

@app.route('../hub/alumni/index.html', methods=['POST'])
def student():

    argv = []

    firstname = request.form.get("firstname")
    argv.append(firstname)
    lastname = request.form.get("lastname")
    argv.append(lastname)
    email = request.form.get("email")
    argv.append(email)
    major = request.form.get("major")
    argv.append(major)
    career = request.form.get("field")
    argv.append(career)

    cursor = mysql.connection.cursor()

    query = "INSERT INTO alumn_table \
             VALUES ? ? ? ? "

    cursor.execute(query, (firstname, lastname, email, major, career))
    mysql.connection.commit() # try and except maybe before
    cursor.close()

#-----------------------------------------------------------------------


if __name__ == '__main__':
    if len(argv) != 2:
        print('Usage: ' + argv[0] + ' port')
        exit(1)
    app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
