#!/usr/bin/env python

#-----------------------------------------------------------------------
# pair.py
# Author: Tara and Abhinaya
#-----------------------------------------------------------------------

from sys import argv
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from flask_mysqldb import MySQL
from test import connection

import yaml

#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='.')
# db = Database(app)

#-----------------------------------------------------------------------
@app.route('/site/pages/student/info', methods=['POST', 'GET'])
def student_info():
    html = render_template('/site/pages/student/info.html')
    return make_response(html)

@app.route('/site/pages/student/profile', methods=['POST', 'GET'])
def student_profile():

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

    print("Testing alumni", argv, sep='\n')
    query = """ INSERT INTO students
                       (StudentInfoNameFirst, StudentInfoNameLast, StudentInfoEmail, StudentAcademicsMajor, StudentCareerDesiredField) VALUES (%s,%s,%s,%s,%s)"""
    # check that the values are correct
    db, conn = connection()
    # db.connect()
    db.execute(query, (firstname, lastname, email, major, career))
    # db.disconnect()
    conn.commit()
    db.close()
    conn.close()
    html = render_template('/site/pages/student/profile.html')
    response = make_response(html)
    return response

#-----------------------------------------------------------------------
@app.route('/site/pages/alumni/info', methods=['POST', 'GET'])
def alumni_info():
    html = render_template('/site/pages/alumni/info.html')
    return make_response(html)


@app.route('/site/pages/alumni/profile', methods=['POST', 'GET'])
def alumni_profile():
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

    print("Testing alumni", argv, sep='\n')

    query = "INSERT INTO alumni \
            VALUES ? ? ? ? ?;"
    # VIKASH
    db = Database()
    db.connect()
    db.execute(query, (firstname, lastname, email, major, career))
    db.disconnect()
    html = render_template('/site/pages/alumni/profile.html')
    response = make_response(html)
    return response


@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
    html = render_template('/site/index.html')
    return make_response(html)

#-----------------------------------------------------------------------

@app.route('/site/pages/signin/index', methods=['GET'])
def matching():
    html = render_template('/site/pages/signin/index.html')
    return make_response(html)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    if len(argv) != 2:
        print('Usage: ' + argv[0] + ' port')
        exit(1)
    app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
    # db = Database(app)
