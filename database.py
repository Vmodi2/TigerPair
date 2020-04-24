from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from config import db


class students(db.Model):
    __tablename__ = 'students'
    studentid = db.Column('studentid', db.Unicode, primary_key=True)
    studentinfonamefirst = db.Column('studentinfonamefirst', db.Unicode)
    studentinfonamelast = db.Column('studentinfonamelast', db.Unicode)
    studentinfoemail = db.Column('studentinfoemail', db.Unicode)
    studentacademicsmajor = db.Column('studentacademicsmajor', db.Unicode)
    studentcareerdesiredfield = db.Column(
        'studentcareerdesiredfield', db.Unicode)
    matched = db.Column('matched', db.SmallInteger)

    def __init__(self, studentid, studentinfonamefirst, studentinfonamelast, studentinfoemail,
                 studentacademicsmajor, studentcareerdesiredfield, matched):
        self.studentid = studentid
        self.studentinfonamefirst = studentinfonamefirst
        self.studentinfonamelast = studentinfonamelast
        self.studentinfoemail = studentinfoemail
        self.studentacademicsmajor = studentacademicsmajor
        self.studentcareerdesiredfield = studentcareerdesiredfield
        self.matched = matched

    # maybe change unicode to string


class alumni(db.Model):
    __tablename__ = 'alumni'
    # alumid = db.Column('alumid', db.Unicode, primary_key=True)
    aluminfonamefirst = db.Column('aluminfonamefirst', db.Unicode)
    aluminfonamelast = db.Column('aluminfonamelast', db.Unicode)
    aluminfoemail = db.Column(
        'aluminfoemail', db.Unicode, primary_key=True, nullable=False)
    alumacademicsmajor = db.Column('alumacademicsmajor', db.Unicode)
    alumcareerfield = db.Column('alumcareerfield', db.Unicode)
    matched = db.Column('matched', db.SmallInteger)
    username = db.Column('username', db.Unicode)
    password = db.Column('password', db.Unicode, nullable=False)
    email_confirmed = db.Column('email_confirmed', db.Boolean)
    authenticated = False

    def __init__(self, aluminfonamefirst, aluminfonamelast, aluminfoemail,
                 alumacademicsmajor, alumcareerfield, username, password,
                 matched, email_confirmed):
        self.aluminfonamefirst = aluminfonamefirst
        self.aluminfonamelast = aluminfonamelast
        self.aluminfoemail = aluminfoemail
        self.alumacademicsmajor = alumacademicsmajor
        self.alumcareerfield = alumcareerfield
        self.matched = matched
        self.username = username
        self.password = password
        self.email_confirmed = email_confirmed

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.email_confirmed

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.aluminfoemail



class matches(db.Model):
    __tablename__ = 'matches'
    studentid = db.Column('studentid', db.Unicode, primary_key=True)
    aluminfoemail = db.Column('aluminfoemail', db.Unicode)

    def __init__(self, studentid, aluminfoemail):
        self.studentid = studentid
        self.aluminfoemail = aluminfoemail
