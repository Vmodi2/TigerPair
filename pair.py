#!/usr/bin/env python

#-----------------------------------------------------------------------
# pair.py
# Author: Tara and Abhinaya
#-----------------------------------------------------------------------

from sys import argv
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from database import Database


#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='.')

#-----------------------------------------------------------------------

@app.route('../hub/student/index.html', methods=['GET'])
@app.route('../hub/alumni/index.html', methods=['GET'])
def student():

    argv = []

    firstname = request.args.get("firstname")
    argv.append(firstname)
    lastname = request.args.get("lastname")
    argv.append(lastname)
    email = request.args.get("email")
    argv.append(email)
    major = request.args.get("major")
    argv.append(major)
    career = request.args.get("field")
    argv.append(career)

    database = Database()
    database.connect()
    database.insert(argv)
