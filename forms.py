
# -----------------------------------------------------------------------
# forms.py
# Used for sign in/up forms that must be validated  both on client and
# server side
# -----------------------------------------------------------------------


from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField, SelectField, IntegerField
from database import alumni, admins
from wtforms.validators import DataRequired, Email, Length, ValidationError, InputRequired, EqualTo, Optional
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

class NewUserForm(Form):
    majors = [("AAS","AAS") ,("ANT","ANT") ,("ARC","ARC") ,("ART","ART") ,("AST","AST") ,("CBE","CBE") ,("CEE","CEE") ,("CHM","CHM") ,("CLA","CLA") ,("COM","COM") ,("COS","COS") ,("EAS","EAS") ,("ECO","ECO") ,("EEB","EEB") ,("ELE","ELE") ,("ENG","ENG") ,("FRE","FRE") ,("GEO","GEO") ,("GER","GER") ,("HIS","HIS") ,("MAE","MAE") ,("MAT","MAT") ,("MOL","MOL") ,("MUS","MUS") ,("NES","NES") ,("NEU","NEU") ,("ORF","ORF") ,("PHI","PHI") ,("PHY","PHY") ,("POL","POL") ,("PSY","PSY") ,("REL","REL") ,("SLA","SLA") ,("SOC","SOC") ,("SPO","SPO") ,("WWS","WWS")]



    careers = [("Accounting","Accounting"), ("Advertising","Advertising"), ("Architecture/Planning","Architecture/Planning"), ("Building/Construction","Building/Construction"), ("Care-Physical","Care-Physical"), ("Consulting","Consulting"), ("Energy Resources","Energy Resources"), ("Engr-Chemical","Engr-Chemical"), ("Engr-Civil","Engr-Civil"), ("Engr-Electrical","Engr-Electrical"), ("Engr-Mech/Aerospace","Engr-Mech/Aerospace"), ("Engr-Other","Engr-Other"), ("Environmental Affairs","Environmental Affairs"), ("Fin-Asset Management","Fin-Asset Management"), ("Fin-Corporate Finance","Fin-Corporate Finance"), ("Fin-Financial Planning","Fin-Financial Planning"), ("Fin-Hedge Funds","Fin-Hedge Funds"), ("Fin-Investestment Banking","Fin-Investestment Banking"), ("Fin-Investment Management","Fin-Investment Management"), ("Fin-Private Equity","Fin-Private Equity"), ("Finance-Commercial Banking","Finance-Commercial Banking"), ("Finance-Other","Finance-Other"), ("Finance-Securities/Commodities","Finance-Securities/Commodities"), ("Finance-Tax","Finance-Tax"), ("Finance-Venture Capital","Finance-Venture Capital"), ("Foreign Service","Foreign Service"), ("Fundraising","Fundraising"), ("Gov-Cabinet Member","Gov-Cabinet Member"), ("Gov-Executive","Gov-Executive"), ("Gov-Legislator","Gov-Legislator"), ("Gov-Other","Gov-Other"), ("Gov-Policy Analysis","Gov-Policy Analysis"), ("Gov-Politics","Gov-Politics"), ("Gov-White House Staff","Gov-White House Staff"), ("Health Care-Mental","Health Care-Mental"), ("Health Care-Other","Health Care-Other"), ("Health","Health"), ("Human","Human"), ("Insurance","Insurance"), ("Law-Corporate","Law-Corporate"), ("Law-Criminal","Law-Criminal"), ("Law-Intellectual Property","Law-Intellectual Property"), ("Law-Litigation","Law-Litigation"), ("Law-Other","Law-Other"), ("Law-Patent/Copyright","Law-Patent/Copyright"), ("Law-Tax","Law-Tax"), ("Law-Trusts and Estates","Law-Trusts and Estates"), ("Marketing","Marketing"), ("Military","Military"), ("Other","Other"), ("Performing Arts","Performing Arts"), ("Printing/Publishing","Printing/Publishing"), ("Public Relations","Public Relations"), ("Radio/TV/Film/Theater","Radio/TV/Film/Theater"), ("Real Estate","Real Estate"), ("Religious Services","Religious Services"), ("Research & Development","Research & Development"), ("Resources","Resources"), ("Sales","Sales"), ("Social Work","Social Work"), ("Sports/Recreation","Sports/Recreation"), ("Teaching-Arts","Teaching-Arts"), ("Teaching-Humanities","Teaching-Humanities"), ("Teaching-Other","Teaching-Other"), ("Teaching-Science/Engr","Teaching-Science/Engr"), ("Teaching-Social Science","Teaching-Social Science"), ("Tech-Biotechnology","Tech-Biotechnology"), ("Tech-E-Commerce","Tech-E-Commerce"), ("Tech-Hardware","Tech-Hardware"), ("Tech-Information Services/Systems","Tech-Information Services/Systems"), ("Tech-Software Dev","Tech-Software Dev"), ("Tech-Telecommunications","Tech-Telecommunications"), ("Technology-Other","Technology-Other"), ("Transportation/Travel","Transportation/Travel"), ("Trust & Estate","Trust & Estate"), ("Veterinary Medicine","Veterinary Medicine"), ("Visual/Fine Arts","Visual/Fine Arts"), ("Writing/Editing","Writing/Editing")]


    firstname = StringField('First Name', validators=[
                         InputRequired(), Length(max=20)])
    lastname = StringField('Last Name', validators=[
                         InputRequired(), Length(max=20)])  #maybe change this
    major = SelectField(choices=majors)
    career = SelectField('Career Field',choices=careers)

    group_id = IntegerField('Group ID', validators=[Optional()])

    group_password = password = PasswordField('Password')


class UserDashboardForm(Form):
    majors = [("AAS","AAS") ,("ANT","ANT") ,("ARC","ARC") ,("ART","ART") ,("AST","AST") ,("CBE","CBE") ,("CEE","CEE") ,("CHM","CHM") ,("CLA","CLA") ,("COM","COM") ,("COS","COS") ,("EAS","EAS") ,("ECO","ECO") ,("EEB","EEB") ,("ELE","ELE") ,("ENG","ENG") ,("FRE","FRE") ,("GEO","GEO") ,("GER","GER") ,("HIS","HIS") ,("MAE","MAE") ,("MAT","MAT") ,("MOL","MOL") ,("MUS","MUS") ,("NES","NES") ,("NEU","NEU") ,("ORF","ORF") ,("PHI","PHI") ,("PHY","PHY") ,("POL","POL") ,("PSY","PSY") ,("REL","REL") ,("SLA","SLA") ,("SOC","SOC") ,("SPO","SPO") ,("WWS","WWS")]



    careers = [("Accounting","Accounting"), ("Advertising","Advertising"), ("Architecture/Planning","Architecture/Planning"), ("Building/Construction","Building/Construction"), ("Care-Physical","Care-Physical"), ("Consulting","Consulting"), ("Energy Resources","Energy Resources"), ("Engr-Chemical","Engr-Chemical"), ("Engr-Civil","Engr-Civil"), ("Engr-Electrical","Engr-Electrical"), ("Engr-Mech/Aerospace","Engr-Mech/Aerospace"), ("Engr-Other","Engr-Other"), ("Environmental Affairs","Environmental Affairs"), ("Fin-Asset Management","Fin-Asset Management"), ("Fin-Corporate Finance","Fin-Corporate Finance"), ("Fin-Financial Planning","Fin-Financial Planning"), ("Fin-Hedge Funds","Fin-Hedge Funds"), ("Fin-Investestment Banking","Fin-Investestment Banking"), ("Fin-Investment Management","Fin-Investment Management"), ("Fin-Private Equity","Fin-Private Equity"), ("Finance-Commercial Banking","Finance-Commercial Banking"), ("Finance-Other","Finance-Other"), ("Finance-Securities/Commodities","Finance-Securities/Commodities"), ("Finance-Tax","Finance-Tax"), ("Finance-Venture Capital","Finance-Venture Capital"), ("Foreign Service","Foreign Service"), ("Fundraising","Fundraising"), ("Gov-Cabinet Member","Gov-Cabinet Member"), ("Gov-Executive","Gov-Executive"), ("Gov-Legislator","Gov-Legislator"), ("Gov-Other","Gov-Other"), ("Gov-Policy Analysis","Gov-Policy Analysis"), ("Gov-Politics","Gov-Politics"), ("Gov-White House Staff","Gov-White House Staff"), ("Health Care-Mental","Health Care-Mental"), ("Health Care-Other","Health Care-Other"), ("Health","Health"), ("Human","Human"), ("Insurance","Insurance"), ("Law-Corporate","Law-Corporate"), ("Law-Criminal","Law-Criminal"), ("Law-Intellectual Property","Law-Intellectual Property"), ("Law-Litigation","Law-Litigation"), ("Law-Other","Law-Other"), ("Law-Patent/Copyright","Law-Patent/Copyright"), ("Law-Tax","Law-Tax"), ("Law-Trusts and Estates","Law-Trusts and Estates"), ("Marketing","Marketing"), ("Military","Military"), ("Other","Other"), ("Performing Arts","Performing Arts"), ("Printing/Publishing","Printing/Publishing"), ("Public Relations","Public Relations"), ("Radio/TV/Film/Theater","Radio/TV/Film/Theater"), ("Real Estate","Real Estate"), ("Religious Services","Religious Services"), ("Research & Development","Research & Development"), ("Resources","Resources"), ("Sales","Sales"), ("Social Work","Social Work"), ("Sports/Recreation","Sports/Recreation"), ("Teaching-Arts","Teaching-Arts"), ("Teaching-Humanities","Teaching-Humanities"), ("Teaching-Other","Teaching-Other"), ("Teaching-Science/Engr","Teaching-Science/Engr"), ("Teaching-Social Science","Teaching-Social Science"), ("Tech-Biotechnology","Tech-Biotechnology"), ("Tech-E-Commerce","Tech-E-Commerce"), ("Tech-Hardware","Tech-Hardware"), ("Tech-Information Services/Systems","Tech-Information Services/Systems"), ("Tech-Software Dev","Tech-Software Dev"), ("Tech-Telecommunications","Tech-Telecommunications"), ("Technology-Other","Technology-Other"), ("Transportation/Travel","Transportation/Travel"), ("Trust & Estate","Trust & Estate"), ("Veterinary Medicine","Veterinary Medicine"), ("Visual/Fine Arts","Visual/Fine Arts"), ("Writing/Editing","Writing/Editing")]


    firstname = StringField('First Name', validators=[
                         InputRequired(), Length(max=20)])
    lastname = StringField('Last Name', validators=[
                         InputRequired(), Length(max=20)])  #maybe change this
    major = SelectField(choices=majors)
    career = SelectField('Career Field',choices=careers)
