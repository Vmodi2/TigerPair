from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__, template_folder='.')

# SQLAlchemy database setup
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://wrmojcmmbmrgbs:1c5df5fe85929a57652b14c8793fb2162f0c1605549df090aa613d2b95da298f@ec2-3-91-112-166.compute-1.amazonaws.com:5432/dan2dlk2ptnidd"
db = SQLAlchemy(app)

class students(db.Model):
    __tablename__ = 'students'
    studentid = db.Column('studentid', db.Unicode, primary_key=True)
    studentinfonamefirst = db.Column('studentinfonamefirst', db.Unicode)
    studentinfonamelast = db.Column('studentinfonamelast', db.Unicode)
    studentinfoemail = db.Column('studentinfoemail', db.Unicode)
    studentacademicsmajor = db.Column('studentacademicsmajor', db.Unicode)
    studentcareerdesiredfield = db.Column('studentcareerdesiredfield', db.Unicode)
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
    
class alumni(db.Model):
    __tablename__ = 'alumni'
    aluminfonamefirst = db.Column('aluminfonamefirst', db.Unicode)
    aluminfonamelast = db.Column('aluminfonamelast', db.Unicode)
    aluminfoemail = db.Column('aluminfoemail', db.Unicode, primary_key=True)
    alumacademicsmajor = db.Column('alumacademicsmajor', db.Unicode)
    alumcareerfield = db.Column('alumcareerfield', db.Unicode)
    matched = db.Column('matched', db.SmallInteger)

    def __init__(self, aluminfonamefirst, aluminfonamelast, aluminfoemail,
                 alumacademicsmajor, alumcareerfield, matched):
        self.aluminfonamefirst = aluminfonamefirst
        self.aluminfonamelast = aluminfonamelast
        self.aluminfoemail = aluminfoemail
        self.alumacademicsmajor = alumacademicsmajor
        self.alumcareerfield = alumcareerfield
        self.matched = matched

class matches(db.Model):
    __tablename__ = 'matches'
    studentid = db.Column('studentid', db.Unicode, primary_key=True)
    aluminfoemail = db.Column('aluminfoemail', db.Unicode)

    def __init__(self, studentid, aluminfoemail):
        self.studentid = studentid
        self.aluminfoemail = aluminfoemail
