#-----------------------------------------------------------------------
# forms.py
# Used for sign in/up forms that must be validated  both on client and
# server side
#-----------------------------------------------------------------------



from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from database import alumni
from wtforms.validators import DataRequired, Email, Length, ValidationError, InputRequired, EqualTo
from werkzeug.security import check_password_hash


# -----------------------------------------------------------------------

class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    #username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

    #def validate_email(self, email):
        #user = alumni.query.filter_by(aluminfoemail=email.data).first()
        #if user is  None:
            #raise ValidationError("Invalid Email")

    #def validate_email(self, email):

        #user = alumni.query.filter_by(aluminfoemail=email.data).first()
        #if not check_password_hash(user.password, password.data):
            #raise ValidationError("Invalid Password")



# -----------------------------------------------------------------------
class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    confirm_password = PasswordField('confirm password', validators=[InputRequired(), EqualTo('password')])

    def validate_email(self, email):
        DOMAIN_ALLOWED= ['princeton.edu']
        email_domain = email.data.split('@')[-1]

        if email_domain not in DOMAIN_ALLOWED:
            raise ValidationError("Must be a princeton address")

        user = alumni.query.filter_by(aluminfoemail = email.data).first()
        if user:
            raise ValidationError("That email is taken. Please use another")




# ------------------------------------------------------------------------
