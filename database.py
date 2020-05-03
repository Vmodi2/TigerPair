from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify
from config import db
from datetime import datetime


class students(db.Model):
    __tablename__ = 'students'
    studentid = db.Column('studentid', db.Unicode, primary_key=True)
    info_firstname = db.Column('info_firstname', db.Unicode)
    info_lastname = db.Column('info_lastname', db.Unicode)
    info_email = db.Column('info_email', db.Unicode)
    academics_major = db.Column('academics_major', db.Unicode)
    career_field = db.Column(
        'career_field', db.Unicode)
    matched = db.Column('matched', db.SmallInteger)
    group_id = db.Column('group_id', db.Unicode)
    last_message = db.Column('last_message', db.DateTime,
                             server_default=str(datetime.utcnow()))
    academics_certificate1 = db.Column('academics_certificate1', db.Unicode)
    academics_certificate2 = db.Column('academics_certificate2', db.Unicode)
    academics_certificate3 = db.Column('academics_certificate3', db.Unicode)
    extracurricular1 = db.Column('extracurricular1', db.Unicode)
    extracurricular2 = db.Column('extracurricular2', db.Unicode)
    extracurricular3 = db.Column('extracurricular3', db.Unicode)
    class_year = db.Column('class_year', db.Unicode)

    def __init__(self, studentid, info_firstname, info_lastname, info_email,
                 academics_major, career_field=None, matched=0, group_id=None):
        self.studentid = studentid
        self.info_firstname = info_firstname
        self.info_lastname = info_lastname
        self.info_email = info_email
        self.academics_major = academics_major
        self.career_field = career_field
        self.matched = matched
        self.group_id = group_id


class alumni(db.Model):
    __tablename__ = 'alumni'
    id = db.Column('id', db.Unicode, db.Sequence(
        'alumni_id_seq'), primary_key=True)
    info_firstname = db.Column('info_firstname', db.Unicode)
    info_lastname = db.Column('info_lastname', db.Unicode)
    info_email = db.Column(
        'info_email', db.Unicode)
    academics_major = db.Column('academics_major', db.Unicode)
    career_field = db.Column('career_field', db.Unicode)
    matched = db.Column('matched', db.SmallInteger)
    password = db.Column('password', db.Unicode)
    email_confirmed = db.Column('email_confirmed', db.Boolean)
    authenticated = False
    group_id = db.Column('group_id', db.Unicode)
    last_message = db.Column('last_message', db.DateTime,
                             server_default=str(datetime.utcnow()))
    academics_certificate1 = db.Column('academics_certificate1', db.Unicode)
    academics_certificate2 = db.Column('academics_certificate2', db.Unicode)
    academics_certificate3 = db.Column('academics_certificate3', db.Unicode)
    extracurricular1 = db.Column('extracurricular1', db.Unicode)
    extracurricular2 = db.Column('extracurricular2', db.Unicode)
    extracurricular3 = db.Column('extracurricular3', db.Unicode)
    class_year = db.Column('class_year', db.Unicode)

    def __init__(self, info_email, info_firstname=None, info_lastname=None, academics_major=None, career_field=None, matched=0, password=None,
                 email_confirmed=False, group_id=None):
        self.info_firstname = info_firstname
        self.info_lastname = info_lastname
        self.info_email = info_email
        self.academics_major = academics_major
        self.career_field = career_field
        self.matched = matched
        self.password = password
        self.email_confirmed = email_confirmed
        self.group_id = group_id

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.email_confirmed

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.info_email


class matches(db.Model):
    __tablename__ = 'matches'
    studentid = db.Column('studentid', db.Unicode, primary_key=True)
    info_email = db.Column('info_email', db.Unicode)
    group_id = db.Column('group_id', db.Unicode)
    contacted = db.Column('contacted', db.Boolean)

    def __init__(self, studentid, info_email, id):
        self.studentid = studentid
        self.info_email = info_email
        self.group_id = id
        self.contacted = False


class admins(db.Model):
    __tablename__ = 'admins'
    id = db.Column('id', db.Unicode, db.Sequence(
        'alumni_id_seq'), primary_key=True)
    username = db.Column('username', db.Unicode)
    group_password = db.Column('group_password', db.Unicode)

    def __init__(self, username):
        self.username = username

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.confirm_email

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username


class groups(db.Model):
    __tablename__ = 'groups'
    id = db.Column('group_id', db.Unicode, primary_key=True)
    adminid = db.Column('admin_id', db.Unicode)
    password = db.Column('password', db.Unicode)

    def __init__(self, group_id, adminid, password):
        self.id = id
        self.group_id = group_id
        self.adminid = adminid
        self.password = password
