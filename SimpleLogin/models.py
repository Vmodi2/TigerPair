from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from config import db

# class students(db.Model):
#     __tablename__ = 'students'
#     studentid = db.Column('studentid', db.Unicode, primary_key=True)
#     studentinfonamefirst = db.Column('studentinfonamefirst', db.Unicode)
#     studentinfonamelast = db.Column('studentinfonamelast', db.Unicode)
#     studentinfoemail = db.Column('studentinfoemail', db.Unicode)
#     studentacademicsmajor = db.Column('studentacademicsmajor', db.Unicode)
#     studentcareerdesiredfield = db.Column('studentcareerdesiredfield', db.Unicode)
#     matched = db.Column('matched', db.SmallInteger)

    # def __init__(self, studentid, studentinfonamefirst, studentinfonamelast, studentinfoemail,
    #              studentacademicsmajor, studentcareerdesiredfield, matched):
    #     self.studentid = studentid
    #     self.studentinfonamefirst = studentinfonamefirst
    #     self.studentinfonamelast = studentinfonamelast
    #     self.studentinfoemail = studentinfoemail
    #     self.studentacademicsmajor = studentacademicsmajor
    #     self.studentcareerdesiredfield = studentcareerdesiredfield
    #     self.matched = matched
    
class alumni(db.Model):
    __tablename__ = 'alumni'
    aluminfonamefirst = db.Column('aluminfonamefirst', db.Unicode)
    aluminfonamelast = db.Column('aluminfonamelast', db.Unicode)
    aluminfoemail = db.Column('aluminfoemail', db.Unicode, primary_key=True)
    alumacademicsmajor = db.Column('alumacademicsmajor', db.Unicode)
    alumcareerfield = db.Column('alumcareerfield', db.Unicode)
    matched = db.Column('matched', db.SmallInteger)
    password = db.Column(db.String(200), nullable=False)
    last_login = db.Column(db.DateTime)

    # def __init__(self, aluminfonamefirst, aluminfonamelast, aluminfoemail,
    #              alumacademicsmajor, alumcareerfield, matched):
    #     self.aluminfonamefirst = aluminfonamefirst
    #     self.aluminfonamelast = aluminfonamelast
    #     self.aluminfoemail = aluminfoemail
    #     self.alumacademicsmajor = alumacademicsmajor
    #     self.alumcareerfield = alumcareerfield
    #     self.matched = matched

    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class admin(db.Model):
    __tablename__ = 'admin'
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class matches(db.Model):
    __tablename__ = 'matches'
    studentid = db.Column('studentid', db.Unicode, primary_key=True)
    aluminfoemail = db.Column('aluminfoemail', db.Unicode)

    def __init__(self, studentid, aluminfoemail):
        self.studentid = studentid
        self.aluminfoemail = aluminfoemail