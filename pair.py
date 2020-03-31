#!/usr/bin/env python

#-----------------------------------------------------------------------
# pair.py
# Author: Vikash and Chris
#-----------------------------------------------------------------------

from sys import argv
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from flask_mysqldb import MySQL
# from test import connection
from database import Database
from stable_marriage import get_matches

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

    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    major = request.form.get("major")
    career = request.form.get("career")


    print("Testing alumni", argv, sep='\n')
    query = """ INSERT INTO students
                       (StudentInfoNameFirst, StudentInfoNameLast, StudentInfoEmail, StudentAcademicsMajor, StudentCareerDesiredField) VALUES (%s,%s,%s,%s,%s)"""
    
    db = Database()
    db.connect()
    db.execute_set(query, (firstname, lastname, email, major, career))
    db.disconnect()

    html = render_template('/site/pages/student/profile.html', firstname=firstname, lastname=lastname, email=email, major=major, career=career)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------
@app.route('/site/pages/alumni/info', methods=['POST', 'GET'])
def alumni_info():
    html = render_template('/site/pages/alumni/info.html')
    return make_response(html)


@app.route('/site/pages/alumni/profile', methods=['POST', 'GET'])
def alumni_profile():

    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    major = request.form.get("major")
    career = request.form.get("career")

    query = """ INSERT INTO alumni\
        (AlumInfoNameFirst, AlumInfoNameLast, AlumInfoEmail, AlumAcademicsMajor, AlumCareerField) VALUES (%s,%s,%s,%s,%s)"""

    db = Database()
    db.connect()
    db.execute_set(query, (firstname, lastname, email, major, career))
    db.disconnect()
    html = render_template('/site/pages/alumni/profile.html', firstname=firstname, lastname=lastname, email=email, major=major, career=career)
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
@app.route('/site/pages/admin/landing', methods=['GET'])
def admin_landing():
    html = render_template('/site/pages/admin/landing.html')
    return make_response(html)

@app.route('/site/pages/admin/matches', methods=['GET'])
def admin_matches():
    matches = get_matches()
    html = render_template('/site/pages/admin/matches.html', matches=matches)
    return make_response(html)

if __name__ == '__main__':
    if len(argv) != 2:
        print('Usage: ' + argv[0] + ' port')
        exit(1)
    app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
    # db = Database(app)