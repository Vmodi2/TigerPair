
# -----------------------------------------------------------------------
# forms.py
# Used for sign in/up forms that must be validated  both on client and
# server side
# -----------------------------------------------------------------------


from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField
from database import alumni, admins
from wtforms.validators import DataRequired, Email, Length, ValidationError, InputRequired, EqualTo
from werkzeug.security import check_password_hash

# -----------------------------------------------------------------------


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(
        message="Invalid Email"), Length(max=50)])
    #username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')
    #
    # def validate_email(self, email):
    #     user = alumni.query.filter_by(info_email=email.data).first()
    #     if user is None and (len(str(email))<50):
    #         raise ValidationError("Invalid Email")


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[
                        InputRequired(), Email(), Length(max=50)])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=8, max=80)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     InputRequired(), EqualTo('password')])

    def validate_email(self, email):
        DOMAIN_ALLOWED = ['princeton.edu']
        email_domain = email.data.split('@')[-1]

        if email_domain not in DOMAIN_ALLOWED:
            raise ValidationError("Must be a princeton address")

        user = alumni.query.filter_by(info_email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please use another")


class AdminLoginForm(FlaskForm):

    username = StringField('Net ID', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')

    # def validate_username(self, username):
    #     user = admins.query.filter_by(username=username.data).first()
    #     if user is None:
    #         raise ValidationError("Invalid username")

# -----------------------------------------------------------------------


class AdminRegisterForm(FlaskForm):
    username = StringField('Net ID', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=8, max=80)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     InputRequired(), EqualTo('password')])

    def validate_username(self, username):
        user = admins.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Net ID in use")

# -----------------------------------------------------------------------


class ForgotForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])

# -----------------------------------------------------------------------


class PasswordResetForum(Form):
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=8, max=80)])

# -----------------------------------------------------------------------


class ChangeEmailForm(Form):
    email1 = StringField('Email', validators=[
                         InputRequired(), Email(), Length(max=50)])
    email2 = StringField('Email', validators=[
                         InputRequired(), Email(), Length(max=50)])

    def validate_email(self, email):
        user = alumni.query.filter_by(info_email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please use another")
# -----------------------------------------------------------------------
