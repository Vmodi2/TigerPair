from flask_login import UserMixin
from . import db

class Role(db.Model, UserMixin):
  __tablename__ = 'roles'
  __table_args__ = {'extend_existing': True}
  id=db.Column(db.Integer, primary_key=True)
  role=db.Column(db.String(5))
  email=db.Column(db.String(40))
  password=db.Column(db.String(255))

class Alum(db.Model, UserMixin):
  __tablename__ = 'alumni'
  __table_args__ = {'extend_existing': True}
  id=db.Column(db.Integer, primary_key=True)
  aluminfonamefirst=db.Column(db.String(20))
  aluminfonamelast=db.Column(db.String(20))
  aluminfoemail=db.Column(db.String(40))
  alumacademicsmajor=db.Column(db.String(3))
  alumcareerfield=db.Column(db.String(30))
  matched=db.Column(db.Integer)

  def __init__(self, aluminfonamefirst, aluminfonamelast, aluminfoemail,
                 alumacademicsmajor, alumcareerfield, matched):
    self.aluminfonamefirst=db.Column(db.String(20))
    self.aluminfonamelast=db.Column(db.String(20))
    self.aluminfoemail=db.Column(db.String(40))
    self.alumacademicsmajor=db.Column(db.String(3))
    self.alumcareerfield=db.Column(db.String(30))
    self.matched=db.Column(db.Integer)

class Student(db.Model, UserMixin):
  __tablename__ = 'students'
  __table_args__ = {'extend_existing': True}
  studentid=db.Column(db.String(20))
  studentinfonamefirst=db.Column(db.String(20))
  studentinfonamelast=db.Column(db.String(20))
  studentinfoemail=db.Column(db.String(40))
  studentacademicsmajor=db.Column(db.String(3))
  studentcareerdesiredfield=db.Column(db.String(30))
  matched=db.Column(db.Integer)
  id=db.Column(db.Integer, primary_key=True)
  
  def __init__(self, studentid, studentinfonamefirst, studentinfonamelast, studentinfoemail,
                 studentacademicsmajor, studentcareerdesiredfield, matched):
    self.studentid=db.Column(db.String(20))
    self.studentinfonamefirst=db.Column(db.String(20))
    self.studentinfonamelast=db.Column(db.String(20))
    self.studentinfoemail=db.Column(db.String(40))
    self.studentacademicsmajor=db.Column(db.String(3))
    self.studentcareerdesiredfield=db.Column(db.String(30))
    self.matched=db.Column(db.Integer)

class Match(db.Model, UserMixin):
  __tablename__ = 'matches'
  __table_args__ = {'extend_existing': True}
  studentid=db.Column(db.String(20), primary_key=True)
  aluminfoemail=db.Column(db.String(40))