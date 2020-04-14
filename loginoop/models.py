from flask_login import UserMixin
from . import db

class Person(UserMixin, db.Model):
    __tablename__ = 'person'
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(20))