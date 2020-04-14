#!/usr/bin/env python

# -----------------------------------------------------------------------
# pair.py
# -----------------------------------------------------------------------

from sys import argv
from flask_bootstrap import Bootstrap
from flask import request, make_response, redirect, url_for
from flask import render_template
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from database import students, alumni, matches
from stable_marriage import get_matches, create_new_matches, clear_matches, clear_match
import yaml
from flask_mail import Message
from itsdangerous import SignatureExpired
from CASClient import CASClient
from config import app, mail, s, db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# -----------------------------------------------------------------------

bootstrap = Bootstrap(app)
login_manager.login_view = 'login'

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
@login_manager.user_loader
def user_loader(user_id):
    return alumni.query.filter_by(aluminfoemail=user_id).first()
# -----------------------------------------------------------------------
# Dynamic page function for student info page call
@app.route('/site/pages/student/', methods=['POST', 'GET'])
def student_info():
    matched = False
    username = CASClient().authenticate()

    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    major = request.form.get("major")
    career = request.form.get("career")

    current = students.query.filter_by(studentid=username).first()

    if firstname is None:
        if current is not None:
            html = render_template('/site/pages/student/index.html',
                                   firstname=current.studentinfonamefirst,
                                   lastname=current.studentinfonamelast,
                                   email=current.studentinfoemail,
                                   major=current.studentacademicsmajor.upper(),
                                   career=current.studentcareerdesiredfield.capitalize(),
                                   side="Student", matched=matched, username=username)

            
        else: 
            html = render_template('/site/pages/student/index.html', firstname="",
                                   lastname="", email="", major="",
                                   career="", side="Student", matched=matched,
                                   username=username)
    else:
        
        if current is not None: # Update row if student is not new
            current.studentinfonamefirst = firstname
            current.studentinfonamelast = lastname
            current.studentinfoemail = email
            current.studentacademicsmajor = major
            current.studentcareerdesiredfield = career
            db.session.commit()
        else: # Otherwise, add new row
            new_student = students(username, firstname, lastname, email, major, career, 0)
            db.session.add(new_student)
            db.session.commit()

        html = render_template('/site/pages/student/index.html',
                               firstname=firstname,
                               lastname=lastname,
                               email=email,
                               major=major.upper(),
                               career=career.capitalize(),
                               side="Student", matched=matched, username=username)
        
    return make_response(html)

# -----------------------------------------------------------------------

# Dynamic page function for student info page call
@app.route('/site/pages/alumni/', methods=['POST', 'GET'])
@login_required
def alumni_info():
    html = ''

    user = alumni.query.filter_by(aluminfoemail=current_user).first()
    if user.email_confirmed:
        matched = False

        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        major = request.form.get("major")
        career = request.form.get("career")

        if firstname is not None:
            user.aluminfonamefirst = firstname
            user.aluminfonamelast = lastname
            user.alumacademicsmajor = major
            user.alumcareerfield = career
            db.session.commit()
            html = render_template('/site/pages/alumni/index.html', firstname=firstname,
                                   lastname=lastname, email=email, major=major.upper(),
                                   career=career.capitalize(), side="Alumni", exists = True,
                                   matched=matched)
        else:
            html = render_template('/site/pages/alumni/index.html', firstname="",
                                   lastname="", email="", major="",
                                   career="", side="Alumni", exists = True, matched=matched)
    else:
        return redirect(url_for('login'))
    
    return make_response(html)
# -----------------------------------------------------------------------

@app.route('/confirm_email/<token>')
def confirm_email(token):

    html = ''
    errormsg = ''
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600) #one hour to confirm
    except SignatureExpired:
        errormsg = 'The token is expired'
        abort(404)

    user = alumni.query.filter_by(aluminfoemail=email).first_or_404() # give email column indexability
    user.email_confirmed = True
    db.session.commit()

    html = render_template('/site/pages/login/confirm_email.html', errormsg = errormsg)
    return make_response(html)
    # add a button in confirm_email that redirects them to login

    # login_user(user)  # Log in as newly created user
    # return redirect(url_for('/site/pages/alumni/index.html')) ## idk where to redirect to

# -----------------------------------------------------------------------
# Dynamic page function for home page of site
@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
    html = render_template('/site/index.html')
    return make_response(html)

# -----------------------------------------------------------------------
# Dynamic page function for sign in page of site
@app.route('/site/pages/signin/', methods=['GET'])
def matching():
    html = render_template('/site/pages/signin/index.html')
    return make_response(html)

@app.route('/site/pages/login/', methods=['GET', 'POST'])
def login():

    # check that user is verified
    form = LoginForm()

    if form.validate_on_submit():
        user = alumni.query.filter_by(username=form.username.data).first()
        if user is not None:
            if user.email_confirmed:
                if check_password_hash(user.password, form.password.data):
                    user.authenticated = True
                    db.session.commit()
                    login_user(user, remember=form.remember.data)
                    return redirect(url_for('alumni_info'))
            else:
                flash("email not verified")

        else:
            flash("Invalid username or password")

    html = render_template('/site/pages/login/login.html', form=form)
    return make_response(html)

# -----------------------------------------------------------------------

@app.route('/site/pages/login/gotoemail', methods=['GET', 'POST'])
def gotoemail():
    return render_template('/site/pages/login/gotoemail.html')

@app.route('/site/pages/login/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        name = form.username.data
        email = form.email.data
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        existing_user = alumni.query.filter_by(aluminfoemail=email).first()
        if existing_user is None:
       
            # email verification code

            token = s.dumps(email, salt='email-confirm')

            msg = Message('Confirm Email', sender= 'tigerpaircontact@gmail.com', recipients=[email])
            link = url_for('confirm_email', token=token, _external=True)
            msg.body= 'Confirmation link is {}'.format(link)
            mail.send(msg)

            # update the database with new user info

            user = alumni(None, None, email, None, None, name, hashed_password, 0, False, False)
            db.session.add(user)
            db.session.commit()  # Create new user

            return redirect(url_for('gotoemail'), code=400)

        flash('A user already exists with that email address.')

    return render_template('/site/pages/login/signup.html', form=form) ## WE NEED TO CREATE SIGNUP.HTML

# -----------------------------------------------------------------------

@app.route('/site/pages/admin/signin', methods=['GET'])
def admin_signin():
    html = render_template('/site/pages/admin/signin.html', side='Admin')
    return make_response(html)

# -----------------------------------------------------------------------
@app.route('/site/pages/admin/register', methods=['GET'])
def admin_register():
    html = render_template('/site/pages/admin/register.html', side='Admin')
    return make_response(html)

# -----------------------------------------------------------------------
@app.route('/site/pages/admin/landing', methods=['GET'])
def admin_landing():
    matches, unmatched_alumni, unmatched_students = get_matches()
    html = render_template('/site/pages/admin/landing.html', matches=matches,
                           unmatched_alumni=unmatched_alumni,
                           unmatched_students=unmatched_students,
                           side='Admin')
    return make_response(html)
# -----------------------------------------------------------------------
# Dynamic page function for admin home page of site
@app.route('/site/pages/admin/landing/run', methods=['GET'])
def admin_landing_run():
    create_new_matches()
    matches, unmatched_alumni, unmatched_students = get_matches()
    html = render_template('/site/pages/admin/landing.html', matches=matches,
                           unmatched_alumni=unmatched_alumni,
                           unmatched_students=unmatched_students,
                           side='Admin')
    return make_response(html)
# -----------------------------------------------------------------------

@app.route('/site/pages/admin/landing/clearall', methods=['GET'])
def admin_landing_clearall():
    clear_matches()
    matches, unmatched_alumni, unmatched_students = get_matches()
    html = render_template('/site/pages/admin/landing.html', matches=None,
                           unmatched_alumni=unmatched_alumni, unmatched_students=unmatched_students, side='Admin')
    return make_response(html)

# -----------------------------------------------------------------------
@app.route('/site/pages/admin/landing/clearone', methods=['GET'])
def admin_landing_clearone():
    clear_match(request.args.get('student'), request.args.get('alum'))
    matches, unmatched_alumni, unmatched_students = get_matches()
    html = render_template('/site/pages/admin/landing.html', matches=matches,
                           unmatched_alumni=unmatched_alumni,
                           unmatched_students=unmatched_students,
                           side='Admin')
    return make_response(html)

# https://copyninja.info/blog/using-url-for-in-flask.html
# ^ for serving static pages

# -----------------------------------------------------------------------
# Runserver client, input port/host server. Returns current request,
#  and site page. As well as what GET/POST request is sent
if __name__ == '__main__':
    if len(argv) != 2:
        print('Usage: ' + argv[0] + ' port')
        exit(1)
    app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
    # db = Database(app)
