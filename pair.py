#!/usr/bin/env python

# -----------------------------------------------------------------------
# pair.py
# -----------------------------------------------------------------------

from sys import argv
import flask
from flask import request, make_response, redirect, url_for, jsonify
from flask import render_template, flash
from flask_mail import Message
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from itsdangerous import SignatureExpired
from CASClient import CASClient
from werkzeug.security import generate_password_hash, check_password_hash
from database import students, alumni, admins, groups, matches
from stable_marriage import *
from config import app, mail, s, db, login_manager
from forms import LoginForm, RegisterForm
from csv import DictReader, reader
from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, ValidationError
import hashlib
import random
from base64 import b64encode
from datetime import datetime
import requests
import json
from re import search

# -----------------------------------------------------------------------

login_manager.login_view = 'login'

# class LoginForm(Form):
# username = StringField('Email', validators=[DataRequired()])
# password = PasswordField('Password', validators=[
# DataRequired(), Length(min=8, max=80)])


class ForgotForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])


class PasswordResetForum(Form):
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=8, max=80)])

# class InfoForm(Form):
    # firstname = StringField('First Name', validators=[DataRequired()])
    # lastname = StringField('Lasr Name', validators=[DataRequired()])
    # major = StringField('Major', validators=[DataRequired()])
    # career = StringField('Career Field', validators=[DataRequired()])


@login_manager.user_loader
def user_loader(user_id):
    return alumni.query.filter_by(aluminfoemail=user_id).first()


@app.route("/student/logout")
# @login_required <- this makes it redirect to login when student logs out
def student_logout():
    casClient = CASClient()
    casClient.authenticate()
    casClient.logout()
    return redirect(url_for("index"))


@app.route("/alum/logout")
@login_required
def alum_logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/admin/logout")
def admin_logout():
    casClient = CASClient()
    # casClient.authenticate()
    casClient.logout()
    return redirect(url_for("index"))
# -----------------------------------------------------------------------


def get_cas():
    username = strip_user(CASClient().authenticate())
    return username


def route_new_student():
    # username = get_cas()
    # current = students.query.filter_by(studentid=username).first()
    # if not current:
    #     student_new()
    pass


@app.route('/student/new')
def student_new():
    username = get_cas()
    html = render_template('pages/student/new.html',
                           student=students.query.filter_by(studentid=username))
    return make_response(html)


def get_student_info():
    username = CASClient().authenticate()
    username = username[0:len(username)-1]
    # adding tigerbook code (grabbed from tigerbook API)

# /*! jQuery Validation Plugin - v1.17.0 - 7/29/2017
# * https://jqueryvalidation.org/
# * Copyright (c) 2017 Jörn Zaefferer; Licensed MIT */
    key = "2c6f9faa30e5f4b2d7d6e6bb54d72861"
    url = f'https://tigerbook.herokuapp.com/api/v1/undergraduates/{username}+TigerPair'
    created = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ').encode('utf-8')

    nonce = ''.join([random.choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/=')
                     for i in range(32)]).encode('utf-8')

    password = key.encode('utf-8')    # use your own from /getkey
    generated_digest = b64encode(hashlib.sha256(
        nonce + created + password).digest())

    generated_digest = str(generated_digest).replace("b\'", '')
    generated_digest = str(generated_digest).replace("\'", '')
    nonce = str(b64encode(nonce)).replace("b\'", '')
    nonce = str(nonce).replace("\'", '')
    created = str(created).replace("b\'", '')
    created = str(created).replace("\'", '')
    headers = {
        'Authorization': 'WSSE profile="UsernameToken"',
        'X-WSSE': 'UsernameToken Username="%s", PasswordDigest="%s", Nonce="%s", Created="%s"' % (username, generated_digest, nonce, created)
    }
    r = requests.get(url, headers=headers)
    if r:
        student_info = json.loads(r.text)
        firstname = student_info['first_name']
        lastname = student_info['last_name']
        email = student_info['email']
        major = student_info['major_code']

        new_student = students(username, firstname, lastname,
                               email, major)
        upsert_student(new_student)


@app.route('/student/dashboard', methods=['POST', 'GET'])
def student_dashboard():
    route_new_student()
    username = get_cas()
    current = students.query.filter_by(studentid=username).first()
    if not current:
        get_student_info()
        current = students.query.filter_by(studentid=username).first()
        html = render_template('pages/student/new.html',
                               student=current)
        return make_response(html)
    else:
        # print("in student dashboard")
        username = get_cas()
        current = students.query.filter_by(studentid=username).first()
        html = render_template('pages/student/dashboard.html',
                               student=current, username=username, side="student")
        return make_response(html)


@app.route('/student/information', methods=['POST'])
def student_information():
    route_new_student()
    username = get_cas()
    group_id = -1
    current = students.query.filter_by(studentid=username).first()
    info = request.form
    if not current:
        try:
            group_id = int(info.get('group_id'))
        except:
            group_id = 0
        if not admins.query.filter_by(id=group_id).first():
            html = render_template(
                'pages/student/new.html', student=current, errorMsg="The group id you specified does not belong to an existing group")
            return make_response(html)
    else:
        group_id = current.group_id
    new_student = students(username, info.get('firstname'), info.get('lastname'),
                           f'{username}@princeton.edu', info.get('major'), info.get('career'), group_id=group_id)
    upsert_student(new_student)
    return redirect(url_for('student_dashboard'))


@app.route('/student/matches', methods=['GET', 'POST'])
def student_matches(match=None):
    route_new_student()
    username = get_cas()

    if not match:
        match = get_match_student(username)

    if request.form.get("action") == "Confirm":
        if match is not None:
            match_item = matches.query.filter_by(studentid=username).first()
            match_item.contacted = True
            db.session.commit()

    contacted = False
    if match is not None:
        contacted = matches.query.filter_by(
            studentid=username).first().contacted

    current = students.query.filter_by(studentid=username).first()
    html = render_template('pages/student/matches.html',
                           match=match, username=username, student=current, side="student",
                           contacted=contacted)

    if request.form.get("message") is not None:
        # Due to database issues (that won't be in the final product) this may not send
        try:
            group_id = current.group_id
            admin = admins.query.filter_by(id=group_id).first()
            email = admin.username + "@princeton.edu"

            message = request.form.get("message")
            msg = Message(
                'TigerPair Student Message', sender='tigerpaircontact@gmail.com', recipients=[email])
            msg.body = message + "\n --- \nThis message was sent to you from the student: " + username
            mail.send(msg)
        except Exception as e:
            pass

    return make_response(html)


@app.route('/student/email', methods=['GET', 'POST'])
def student_email():
    # check model to see if you can modify current_user directly
    # TODO CONFIRM EMAIL IS PRINCETON AND MAKE SURE THE EMAILS ARE THE SAME
    route_new_student()
    username = get_cas()
    current = students.query.filter_by(
        studentid=username).first()
    errorMsg = ''
    email1 = request.form.get('email')
    email2 = request.form.get('email-repeated')
    if not email1 == email2:
        errorMsg = "Your emails must match"
    elif not verify_email_regex(request):
        errorMsg = "Please enter a valid email address"
    elif students.query.filter_by(studentinfoemail=email1).first():
        errorMsg = "That email already belongs to another account"
    else:
        current.studentinfoemail = email1
        db.session.commit()
    html = render_template('pages/student/dashboard.html',
                           active_email=True, errorMsg=errorMsg, student=current, side="student")
    return make_response(html)


@app.route('/student/id', methods=['GET', 'POST'])
def student_id():
    # check model to see if you can modify current_user directly
    # TODO CONFIRM EMAIL IS PRINCETON AND MAKE SURE THE EMAILS ARE THE SAME
    route_new_student()
    username = get_cas()
    current = students.query.filter_by(
        studentid=username).first()
    response = {}
    if request.method == "POST":
        if matches.query.filter_by(studentid=username).first():
            response['msg'] = 'You may not change groups while you are matched'
        else:
            new_id = request.form.get('id').strip()
            if new_id:
                group = admins.query.filter_by(id=new_id).first()
                if group:
                    current.group_id = new_id
                    db.session.commit()
                    response['changed'] = True
                    response['id'] = new_id
                    response['msg'] = 'Success changing your group!'
                else:
                    response['msg'] = 'The chosen group id does not belong to an existing group'
    else:
        response['msg'] = 'An unexpected error occurred'
    return jsonify(response)


@app.route('/student/account', methods=['GET'])
def student_account():
    route_new_student()
    username = get_cas()
    current = students.query.filter_by(studentid=username).first()
    html = render_template('pages/student/account.html',
                           active_email=True, username=username, student=current, side="student")
    return make_response(html)


@app.route('/student/delete', methods=['GET'])
def student_delete():
    username = get_cas()
    # find if matched already and delete current match could use clear match
    # but then I would have to find student object
    alum = get_match_student(username=username)
    if alum is not None:
        alum.matched -= 1
        matches.query.filter_by(studentid=username).delete()
    students.query.filter_by(studentid=username).delete()
    db.session.commit()
    return redirect(url_for('index'))


def get_match_student(username):
    match = matches.query.filter_by(studentid=username).first()
    if not match:
        return None
    return alumni.query.filter_by(aluminfoemail=match.aluminfoemail).first()
# -----------------------------------------------------------------------

# Dynamic page function for alum info page call

# WHY DO WE NEED THIS FUNCTION? Alumn info is trying to get info from
# a form that does not exist until dashboard is called but we  call information first?

# @app.route('/alum/dashboard', methods=['POST', 'GET'])
# @login_required
# def alum_dashboard():
    # if not current_user.email_confirmed:
    # return redirect(url_for('login'))
    # html = render_template('pages/alum/dashboard.html',
    # alum=current_user, username=current_user.aluminfoemail, side="alum")
    # return make_response(html)

# NEW ALUM START
@app.route('/alum/dashboard', methods=['GET', 'POST'])
@login_required
def alumni_dashboard():
    if not current_user.email_confirmed:
        return redirect(url_for('gotoemail'))
    current = alumni.query.filter_by(
        aluminfoemail=current_user.aluminfoemail).first()
    if not current.aluminfonamefirst:
        html = render_template('pages/alum/new.html',
                               user=current, username=current.aluminfoemail, side="alum")
    else:
        html = render_template('pages/alum/dashboard.html', alum=current_user,
                               username=current_user.aluminfoemail, side="alum")
    return make_response(html)


@app.route('/alum/information', methods=['GET', 'POST'])
@login_required
def alumni_info():
    if not current_user.email_confirmed:
        return redirect(url_for('gotoemail'))
    if (flask.request.method == 'POST'):
        alum = alumni.query.filter_by(
            aluminfoemail=current_user.aluminfoemail).first()
        alum.aluminfonamefirst = request.form.get('firstname')
        alum.aluminfonamelast = request.form.get('lastname')
        alum.alumacademicsmajor = request.form.get('major')
        alum.alumcareerfield = request.form.get('career')
        try:
            alum.group_id = int(request.form.get('group_id'))
        except:
            alum.group_id = 0
        db.session.commit()
    return redirect(url_for('alumni_dashboard'))


@app.route('/alum/email', methods=['GET', 'POST'])
@login_required
def alumni_email():
    # check model to see if you can modify current_user directly
    # TODO CONFIRM EMAIL IS PRINCETON AND MAKE SURE THE EMAILS ARE THE SAME
    if current_user.aluminfonamefirst is None:
        return redirect(url_for('alumni_dashboard'))
    current = alumni.query.filter_by(
        aluminfoemail=current_user.aluminfoemail).first()
    errorMsg = ''
    email1 = request.form.get('email')
    email2 = request.form.get('email-repeated')
    if email1 != email2:
        errorMsg = "Your emails must match"
    elif not verify_email_regex(request):
        errorMsg = "Please enter a valid email address"
    elif alumni.query.filter_by(aluminfoemail=email1).first():
        errorMsg = "That email already belongs to another account"
    else:
        current.aluminfoemail = email1
        current_user.aluminfoemail = email1
        db.session.commit()
        return redirect(url_for('alum_logout'))
    html = render_template('pages/alum/dashboard.html',
                           active_email=True, errorMsg=errorMsg, alum=current, side="alum")
    return make_response(html)


@app.route('/alum/id', methods=['GET', 'POST'])
@login_required
def alumni_id():
    # check model to see if you can modify current_user directly
    # TODO CONFIRM EMAIL IS PRINCETON AND MAKE SURE THE EMAILS ARE THE SAME
    if current_user.aluminfonamefirst is None:
        return redirect(url_for('alumni_dashboard'))
    current = alumni.query.filter_by(
        aluminfoemail=current_user.aluminfoemail).first()
    response = {}
    if request.method == "POST":
        if matches.query.filter_by(aluminfoemail=current_user.aluminfoemail).first():
            response['msg'] = 'You may not change groups while you are matched'
        else:
            new_id = request.form.get('id').strip()
            if new_id:
                group = admins.query.filter_by(id=new_id).first()
                if group:
                    current.group_id = new_id
                    db.session.commit()
                    response['changed'] = True
                    response['id'] = new_id
                    response['msg'] = 'Success changing your group!'
                else:
                    response['msg'] = 'The chosen group id does not belong to an existing group'
    else:
        response['msg'] = 'An unexpected error occurred'
    return jsonify(response)


@app.route('/alum/matches', methods=['GET', 'POST'])
@login_required
def alum_matches(match=None):
    # username = get_cas()
    if current_user.aluminfonamefirst is None:
        return redirect(url_for('alumni_dashboard'))
                        
    if not match:
        match = get_match_alum(current_user.aluminfoemail)

    if request.form.get("action") == "Confirm":
        if match is not None:
            match_item = matches.query.filter_by(
                studentid=match.studentid).first()
            match_item.contacted = True
            db.session.commit()

    contacted = False
    if match is not None:
        contacted = matches.query.filter_by(
            studentid=match.studentid).first().contacted

    html = render_template('pages/alum/matches.html', username=current_user.aluminfoemail, alum=current_user,
                           match=match, side="alum",
                           contacted=contacted)

    if request.form.get("message") is not None:
        # Due to database issues (that won't be in the final product) this may not send
        try:
            group_id = current_user.group_id
            admin = admins.query.filter_by(id=group_id).first()
            email = admin.username + "@princeton.edu"

            message = request.form.get("message")
            msg = Message(
                'TigerPair Student Message', sender='tigerpaircontact@gmail.com', recipients=[email])
            msg.body = message + "\n --- \nThis message was sent to you from the student: " + \
                current_user.aluminfonamefirst + " " + current_user.aluminfonamelast
            mail.send(msg)
        except Exception as e:
            pass

    return make_response(html)


@app.route('/alum/account', methods=['GET'])
@login_required
def alum_account():
    if current_user.aluminfonamefirst is None:
        return redirect(url_for('alumni_dashboard'))
    username = current_user.aluminfoemail
    current = alumni.query.filter_by(aluminfoemail=username).first()
    html = render_template('pages/alum/account.html',
                           active_email=True, username=username, alum=current, side="alum")
    return make_response(html)


@app.route('/alum/delete', methods=['GET'])
@login_required
def alum_delete():
    if current_user.aluminfonamefirst is None:
        return redirect(url_for('alumni_dashboard'))
    email = current_user.aluminfoemail
    # find if matched already and delete current match
    student = get_match_alum(email=email)
    if student is not None:
        student.matched = 0
        matches.query.filter_by(aluminfoemail=email).delete()
    alumni.query.filter_by(aluminfoemail=email).delete()
    db.session.commit()
    return redirect(url_for('index'))


def get_match_alum(email):
    match = matches.query.filter_by(aluminfoemail=email).first()
    if not match:
        return None
    return students.query.filter_by(studentid=match.studentid).first()


def verify_email_regex(request):
    email1 = request.form.get('email')
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    return search(regex, email1)




# NEW ALUM END
# -----------------------------------------------------------------------


@app.route('/confirm_email/<token>')
def confirm_email(token):

    html = ''
    errormsg = ''
    try:
        # changed to infinite (got rid of max_age)
        # email = s.loads(token, salt='email-confirm', max_age=3600)
        email = s.loads(token, salt='email-confirm')
    except SignatureExpired:
        errormsg = 'The token is expired'
        abort(404)

    # give email column indexability
    user = alumni.query.filter_by(aluminfoemail=email).first_or_404()
    user.email_confirmed = True
    db.session.commit()

    html = render_template(
        'pages/login/confirm_email.html', errormsg=errormsg)
    return make_response(html)
    # add a button in confirm_email that redirects them to login

    # login_user(user)  # Log in as newly created user
    # return redirect(url_for('/site/pages/alumni/index.html')) ## idk where to redirect to

# -----------------------------------------------------------------------
# Dynamic page function for home page of site
@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
    html = render_template('pages/index.html', side="landing")
    return make_response(html)


@app.route('/team', methods=['GET'])
def team():
    return render_template('pages/team.html')


@app.route('/admin-info', methods=['GET'])
def admininfo():
    return render_template('pages/admininfo.html')

# -----------------------------------------------------------------------
# Dynamic page function for sign in page of site
@app.route('/signin', methods=['GET'])
def matching():
    html = render_template('pages/signin/index.html')
    return make_response(html)


@app.route('/login', methods=['POST', 'GET'])
def login():
    # print("login")
    if current_user.is_authenticated:
        return redirect(url_for('alumni_info'))

    form = LoginForm()
    if form.validate_on_submit():
        # print("submitted form")
        user = alumni.query.filter_by(aluminfoemail=form.email.data).first()
        if user is not None:
            # print("user is not none")
            if user.email_confirmed:
                # print("email is confirmed")
                if check_password_hash(user.password, form.password.data):
                    # print("password is correct")
                    db.session.commit()
                    login_user(user, remember=form.remember.data)
                    return redirect(url_for('alumni_info'))
                    # url_for('alum_info')
            else:
                flash("email not verified")

        else:
            flash("Invalid username or password")

    html = render_template('pages/login/login.html', form=form)
    return make_response(html)

# -----------------------------------------------------------------------

# THIS IS NEW !!!!!!!
@app.route('/pages/login/update', methods=['GET', 'POST'])
def update():
    form = ForgotForm()
    if form.validate_on_submit():
        email = form.email.data
        user = alumni.query.filter_by(aluminfoemail=email).first()
        if user is not None:

            token = s.dumps(email, salt='password-update')

            msg = Message(
                'Update Password', sender='tigerpaircontact@gmail.com', recipients=[email])
            link = url_for('update_password', token=token, _external=True)
            msg.body = 'Click here to update password {}'.format(link)
            mail.send(msg)
            return redirect(url_for('gotoemail'))

        else:
            flash("Invalid credentials")

    html = render_template(
        'pages/login/email_update.html', form=form)  # MAKE THIS
    return make_response(html)

# -----------------------------------------------------------------------


@app.route('/login/password-update/<token>', methods=['GET', 'POST'])
def update_password(token):

    html = ''
    errormsg = ''
    try:
        email = s.loads(token, salt='password-update',
                        max_age=3600)  # one hour to confirm
    except SignatureExpired:
        errormsg = 'The token is expired'
        abort(404)

    form = PasswordResetForum()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        user = alumni.query.filter_by(aluminfoemail=email).first_or_404()
        user.password = hashed_password
        db.session.commit()
        return redirect(url_for('password_changed'))

    html = render_template(
        'pages/login/password-update.html', errormsg=errormsg, form=form)  # MAKE THIS ALSO
    return make_response(html)

# -----------------------------------------------------------------------


@app.route('/login/password_changed')
def password_changed():
    html = render_template('pages/login/password_changed.html')
    return make_response(html)

# -----------------------------------------------------------------------


@app.route('/login/gotoemail', methods=['GET', 'POST'])
def gotoemail():
    return render_template('pages/login/gotoemail.html')


@app.route('/login/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data
        # username = form.username.data
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        existing_user = alumni.query.filter_by(aluminfoemail=email).first()
        if existing_user is None:

            # email verification code

            token = s.dumps(email, salt='email-confirm')

            msg = Message(
                'Confirm Email', sender='tigerpaircontact@gmail.com', recipients=[email])
            link = url_for('confirm_email', token=token, _external=True)
            msg.body = 'Confirmation link is {}'.format(link)
            mail.send(msg)

            # update the database with new user info

            user = alumni(email, password=hashed_password)
            upsert_alum(user)

            return redirect(url_for('gotoemail'))

        flash('A user already exists with that email address.')

    html = render_template('pages/login/signup.html', form=form)
    return make_response(html)

# -----------------------------------------------------------------------


def verify_admin():
    username = get_cas()
    current = admins.query.filter_by(username=username).first()
    if not current:
        current = admins(username)
        db.session.add(current)
        db.session.commit()
    return username, current.id


@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    username, id = verify_admin()
    matches = get_matches(id)
    html = render_template('pages/admin/dashboard.html', matches=matches,
                           side='admin', username=username, id=id)
    return make_response(html)

# -----------------------------------------------------------------------
# Dynamic page function for admin home page of site
@app.route('/admin/dashboard/create', methods=['GET'])
def admin_dashboard_create():
    username, id = verify_admin()
    create_new_matches(id)
    return redirect(url_for('admin_dashboard'))
# -----------------------------------------------------------------------


@app.route('/admin/modify-matches', methods=['GET'])
def admin_dashboard_modify_matches():
    username, id = verify_admin()
    html = render_template('pages/admin/modify-matches.html', matches=matches,
                           side='admin', username=username, id=id)
    return make_response(html)


@app.route('/admin/dashboard/clearall', methods=['GET'])
def admin_dashboard_clearall():
    username, id = verify_admin()
    clear_matches(id)
    return redirect(url_for('admin_dashboard'))

# -----------------------------------------------------------------------
@app.route('/admin/dashboard/clearone', methods=['GET'])
def admin_dashboard_clearone():
    username, id = verify_admin()
    clear_match(request.args.get('student'), request.args.get('alum'))
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/manual-match', methods=['GET'])
def admin_dashboard_manual_match():
    username, id = verify_admin()
    alumni = get_unmatched_alumni(id)
    students = get_unmatched_students(id)
    html = render_template('pages/admin/manual-match.html', alumni=alumni, students=students,
                           side='admin', username=username, id=id)
    return make_response(html)


@app.route('/admin/dashboard/createone', methods=['POST', 'GET'])
def admin_dashboard_createone():
    username, id = verify_admin()
    create_one(id, request.form.get('student'), request.form.get('alum'))
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/profiles-alum')
def admin_profiles_alum():
    username, id = verify_admin()
    alumni = get_alumni(id)
    html = render_template('pages/admin/profiles-alum.html', alumni=alumni,
                           side='admin', username=username, id=id)
    return make_response(html)

# SINGLE alum profile page
@app.route('/admin/profile-alum')
def admin_profile_alum():
    username, id = verify_admin()
    alum, matches = get_alum(request.args['email'])
    html = render_template('pages/admin/profile-alum.html',
                           alum=alum, matches=matches,
                           side='admin', username=username, id=id)
    return make_response(html)


@app.route('/admin/profiles-student')
def admin_profiles_student():
    username, id = verify_admin()
    students = get_students(id)
    html = render_template(
        'pages/admin/profiles-student.html', students=students,
        side='admin', username=username, id=id)
    return make_response(html)

# SINGLE student profile page
@app.route('/admin/profile-student')
def admin_profile_student():
    username, id = verify_admin()
    student, matches = get_student(request.args['netid'])
    html = render_template('pages/admin/profile-student.html',
                           student=student, matches=matches,
                           side='admin', username=username, id=id)
    return make_response(html)


@app.route('/admin/get-registrations-alum', methods=['GET'])
def admin_get_registrations_alum():
    username, id = verify_admin()
    registrations = db.engine.execute(
        "SELECT DISTINCT (DATE(date_created)) AS unique_date, COUNT(*) AS amount FROM alumni GROUP BY unique_date ORDER BY unique_date ASC;")
    response = {str(row[0]): row[1] for row in registrations}
    return jsonify(response)


@app.route('/admin/get-registrations-student', methods=['GET'])
def admin_get_registrations_student():
    username, id = verify_admin()
    registrations = db.engine.execute(
        "SELECT DISTINCT (DATE(date_created)) AS unique_date, COUNT(*) AS amount FROM students GROUP BY unique_date ORDER BY unique_date ASC;")
    response = {str(row[0]): row[1] for row in registrations}
    return jsonify(response)


@app.route('/admin/import-students')
def admin_import_students():
    username, id = verify_admin()
    html = render_template('pages/admin/import-students.html',
                           side="Admin", username=username, id=id)
    return make_response(html)


@app.route('/admin/import-alumni')
def admin_import_alumni():
    username, id = verify_admin()
    html = render_template('pages/admin/import-alumni.html',
                           side="Admin", username=username, id=id)
    return make_response(html)


@app.route('/admin/import-students/process', methods=["POST"])
def admin_import_students_process():
    username, id = verify_admin()
    return process_import(is_alumni=False)


@app.route('/admin/import-alumni/process', methods=["POST"])
def admin_import_alumni_process():
    username, id = verify_admin()
    return process_import(is_alumni=True)


def process_import(is_alumni):
    username, id = verify_admin()
    try:
        request_file = request.files['data_file']
        if not request_file:
            return "No file"
        csv_reader = DictReader(chunk.decode() for chunk in request_file)
        if is_alumni:
            for row in csv_reader:
                new_alum = alumni(aluminfonamefirst=row['First Name'], aluminfonamelast=row['Last Name'],
                                  aluminfoemail=row['Email'], alumacademicsmajor=row['Major'].upper(), alumcareerfield=row['Career'], group_id=id)
                print(new_alum.group_id)
                upsert_alum(new_alum)
        else:
            for row in csv_reader:
                new_student = students(row['netid'], row['First Name'],
                                       row['Last Name'], row['Email'], row['Major'].upper(), row['Career'], group_id=id)
                upsert_student(new_student)
        db.session.commit()
        return make_response("Success processing your upload!")
    except Exception as e:
        return make_response("Error processing your upload. It's possible that you are attempting to upload duplicate information.\n" + str(e))


@app.route('/admin/action-student', methods=["POST"])
def admin_action_student():
    username, id = verify_admin()
    if request.form.get('action') == 'delete':
        students = request.form.get('checked-members').split(',')
        for student in students:
            delete_student(id, student)
    return redirect(url_for('admin_profiles_student'))


@app.route('/admin/action-alum', methods=["POST"])
def admin_action_alum():
    username, id = verify_admin()
    if request.form.get('action') == 'delete':
        alumni = request.form.get('checked-members').split(',')
        for alum in alumni:
            delete_alum(id, alum)
    return redirect(url_for('admin_profiles_alum'))


# REDIRECT HERE FROM THE BUTTON
# @app.route('/admin/group-login', methods=['GET', 'POST'])
# def login():

    # form = LoginForm()
    # if form.validate_on_submit():
    # group_id = groups.query.filter_by(group_id=form.group_id.data).first()
    # if group_id is not None:
    # if check_password_hash(user.password, form.password.data): We should hash group_ids for safety
    # login_user(user, remember=form.remember.data)
    # return redirect(url_for('/admin/dashboard'))
    # else:
    # flash("Group ID does not exist")

    # html = render_template('pages/admin/group-login.html', form=form)
    # return make_response(html)


def strip_user(username):
    return username.replace('\n', '')


def upsert_student(student):
    table_student = students.query.filter_by(
        studentid=student.studentid).first()
    if table_student:
        table_student.studentinfonamefirst = student.studentinfonamefirst
        table_student.studentinfonamelast = student.studentinfonamelast
        table_student.studentinfoemail = student.studentinfoemail
        table_student.studentacademicsmajor = student.studentacademicsmajor
        table_student.studentcareerdesiredfield = student.studentcareerdesiredfield
        table_student.group_id = student.group_id
    else:
        db.session.add(student)
    db.session.commit()


def upsert_alum(alum):
    table_alum = alumni.query.filter_by(
        aluminfoemail=alum.aluminfoemail).first()
    if table_alum:
        table_alum.aluminfonamefirst = alum.aluminfonamefirst
        table_alum.aluminfonamelast = alum.aluminfonamelast
        table_alum.aluminfoemail = alum.aluminfoemail
        table_alum.alumacademicsmajor = alum.alumacademicsmajor
        table_alum.alumcareerfield = alum.alumcareerfield
        table_alum.group_id = alum.group_id
    else:
        db.session.add(alum)
    db.session.commit()


# ---------------------------------------------------------------------

# THIS IS WHERE THE ADMIN INTERFACE BEGINS!

# @app.route('/login/admin', methods=['POST', 'GET'])
# def adminlogin():
#     # print("login")

#     form = LoginForm()
#     if form.validate_on_submit():
#         # print("submitted form")
#         user = admins.query.filter_by(adminusername=form.username.data).first() ## CHECK DATABASE.PY
#         if user is not None:
#             # print("user is not none")

#             # print("email is confirmed")
#             if check_password_hash(user.password, form.password.data):
#                 # print("password is correct")
#                 db.session.commit() # could we remove this
#                 login_user(user, remember=form.remember.data)
#                 return redirect(url_for('alumni_info'))
#                 # url_for('alum_info')


#         else:
#             flash("Invalid username or password")

#     html = render_template('pages/login/login.html', form=form)
#     return make_response(html)

# @app.route('/login/asignup', methods=['GET', 'POST'])
# def signup():
#     form = RegisterForm()

#     if form.validate_on_submit():
#         email = form.email.data
#         # username = form.username.data
#         hashed_password = generate_password_hash(
#             form.password.data, method='sha256')
#         existing_user = alumni.query.filter_by(aluminfoemail=email).first()
#         if existing_user is None:
#             if user.email_confirmed:

#             # email verification code

#                 token = s.dumps(email, salt='email-confirm')

#                 msg = Message(
#                     'Confirm Email', sender='tigerpaircontact@gmail.com', recipients=[email])
#                 link = url_for('confirm_email', token=token, _external=True)
#                 msg.body = 'Confirmation link is {}'.format(link)
#                 mail.send(msg)

#                 # update the database with new user info

#                 user = alumni(email, password=hashed_password)
#                 upsert_alum(user)

#                 return redirect(url_for('gotoemail'))

#         flash('A user already exists with that email address.')

#     html = render_template('pages/login/signup.html', form=form)
#     return make_response(html)


# -----------------------------------------------------------------------
# Runserver client, input port/host server. Returns current request,
#  and site page. As well as what GET/POST request is sent
if __name__ == '__main__':
    if len(argv) != 2:
        print('Usage: ' + argv[0] + ' port')
        exit(1)
    # 32 MB maximum in memory reserved for uploads
    app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
    # db = Database(app)
