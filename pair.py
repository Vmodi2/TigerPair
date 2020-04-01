#!/usr/bin/env python

#-----------------------------------------------------------------------
# pair.py
# Author: Tara, Abhinaya, Vikash, and Chris
#-----------------------------------------------------------------------

from sys import argv
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from flask_mysqldb import MySQL
# from test import connection
from database import Database
from stable_marriage import get_matches, create_new_matches, clear_matches, clear_match

import yaml

#-----------------------------------------------------------------------
# Global var for program name
app = Flask(__name__, template_folder='.')
# db = Database(app)

#-----------------------------------------------------------------------
# Dynamic page function for student info page call
@app.route('/site/pages/student/info', methods=['POST', 'GET'])
def student_info():
    html = render_template('/site/pages/student/info.html')
    return make_response(html)
# Dynamic Function for student profile page call
# Request values from the profile info form, and 
# Set up query to add row to Student table
@app.route('/site/pages/student/profile', methods=['POST', 'GET'])
def student_profile():
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    major = request.form.get("major")
    career = request.form.get("career")


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

# Dynamic page function for student info page call
@app.route('/site/pages/alumni/info', methods=['POST', 'GET'])
def alumni_info():
    html = render_template('/site/pages/alumni/info.html')
    return make_response(html)

# Dynamic Function for alumni profile page call
# Request values from the profile info form, and 
# Set up query to add row to Alumni table.
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


# Dynamic page function for home page of site
@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
    html = render_template('/site/index.html')
    return make_response(html)

#-----------------------------------------------------------------------
# Dynamic page function for sign in page of site
@app.route('/site/pages/signin/index', methods=['GET'])
def matching():
    html = render_template('/site/pages/signin/index.html')
    return make_response(html)

#-----------------------------------------------------------------------
# Dynamic page function for admin home page of site
@app.route('/site/pages/admin/landing', methods=['GET'])
def admin_landing():
    html = render_template('/site/pages/admin/landing.html')
    return make_response(html)
# Dynamic page function for admin matches page of site
# request a stable marriage pairing between all listed
# students and alumni. Display in table on this page.
@app.route('/site/pages/admin/matches', methods=['GET'])
def admin_matches():
    create_new_matches()
    matches, unmatched_alumni, unmatched_students = get_matches()
    html = render_template('/site/pages/admin/matches.html', matches=matches, unmatched_alumni=unmatched_alumni, unmatched_students=unmatched_students)
    return make_response(html)

@app.route('/site/pages/admin/matches/clearall', methods=['GET'])
def admin_matches_clearall():
    clear_matches()
    html = render_template('/site/pages/admin/matches.html', matches=None)
    return make_response(html)

@app.route('/site/pages/admin/matches/clearone', methods=['GET'])
def admin_matches_clearone():
    clear_match(request.args.get('student'), request.args.get('alum'))
    matches, unmatched_alumni, unmatched_students = get_matches()
    html = render_template('/site/pages/admin/matches.html', matches=matches, unmatched_alumni=unmatched_alumni, unmatched_students=unmatched_students)
    return make_response(html)

# https://copyninja.info/blog/using-url-for-in-flask.html
# ^ for serving static pages

# Runserver client, input port/host server. Returns current request,
#  and site page. As well as what GET/POST request is sent
if __name__ == '__main__':
    if len(argv) != 2:
        print('Usage: ' + argv[0] + ' port')
        exit(1)
    app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
    # db = Database(app)