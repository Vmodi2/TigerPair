#!/usr/bin/env python

#-----------------------------------------------------------------------
# pair.py
# Author: Vikash 
#-----------------------------------------------------------------------
# THIS IS A TEST IMPLMENTATION OF PAIR.PY DO NOT USE
from sys import argv
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from flask_mysqldb import MySQL
# from test import connection
from database import Database

import yaml

#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='.')
app.secret_key = b'\xcdt\x8dn\xe1\xbdW\x9d[}yJ\xfc\xa3~/'
# db = Database(app)

#-----------------------------------------------------------------------
@app.route('/site/pages/student/info', methods=['POST', 'GET'])
def student_info():
    username = CASClient().authenticate()
    html = render_template('/site/pages/student/info.html', username=username)
    return make_response(html)

@app.route('/site/pages/student/profile', methods=['POST', 'GET'])
def student_profile():
    username = CASClient().authenticate()
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    major = request.form.get("major")
    career = request.form.get("career")


    print("Testing alumni", argv, sep='\n')
    query = """ INSERT INTO students
                       (StudentInfoNameFirst, StudentInfoNameLast, StudentInfoEmail, StudentAcademicsMajor, StudentCareerDesiredField) VALUES (%s,%s,%s,%s,%s)"""
    # db is cursor, conn is connection
    db, conn = connection()

    db.execute(query, (firstname, lastname, email, major, career))

    conn.commit()
    db.close()
    conn.close()
    html = render_template('/site/pages/student/profile.html', firstname=firstname, lastname=lastname, email=email, major=major, career=career, username=username)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------
@app.route('/site/pages/alumni/info', methods=['POST', 'GET'])
def alumni_info():
    username = CASClient().authenticate()
    html = render_template('/site/pages/alumni/info.html', username=username)
    return make_response(html)


@app.route('/site/pages/alumni/profile', methods=['POST', 'GET'])
def alumni_profile():
    username = CASClient().authenticate()
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    major = request.form.get("major")
    career = request.form.get("career")

    query = """ INSERT INTO alumni\
        (AlumInfoNameFirst, AlumInfoNameLast, AlumInfoEmail, AlumAcademicsMajor, AlumCareerField) VALUES (%s,%s,%s,%s,%s)"""

   # check that the values are correct
    # db, conn = connection()

    # conn.commit()
    # db.close()
    # conn.close()
    db = Database()
    db.connect()
    db.execute_set(query, (firstname, lastname, email, major, career))
    db.disconnect()
    html = render_template('/site/pages/alumni/profile.html', firstname=firstname, lastname=lastname, email=email, major=major, career=career, username=username)
    response = make_response(html)
    return response



@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
    html = render_template('/site/index.html', )
    return make_response(html)

#-----------------------------------------------------------------------

@app.route('/site/pages/signin/index', methods=['GET'])
def matching():
    username = CASClient().authenticate()
    html = render_template('/site/pages/signin/index.html', username=username)
    return make_response(html)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    if len(argv) != 2:
        print('Usage: ' + argv[0] + ' port')
        exit(1)
    app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
    # db = Database(app)