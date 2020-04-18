from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import InputRequired, Email, Length

# -----------------------------------------------------------------------

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')
    
# -----------------------------------------------------------------------

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

# -----------------------------------------------------------------------

MAJORS = [	"AAS", "ANT", "ARC", "ART", "AST", "CBE", "CEE", "CHM", "CLA", "COM", "COS", "EAS",
				"ECO", "EEB", "ELE", "ENG", "FRE", "GEO", "GER", "HIS", "MAE", "MAT", "MOL", "MUS",
				"NES", "NEU", "ORF", "PHI", "PHY", "POL", "PSY", "REL", "SLA", "SOC", "SPO", "WWS" ]

class StudentInfoForm(FlaskForm):
    firstname = StringField('firstname', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    lastname = StringField('lastname', validators=[InputRequired(), Length(min=4, max=15)])
    email = StringField('email', validators=[InputRequired(), Length(min=8, max=80)])
    major = SelectField('major', choices = [major for major in MAJORS])
    career = StringField('password', validators=[InputRequired(), Length(min=8, max=80)])
# -----------------------------------------------------------------