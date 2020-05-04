#!/usr/bin/env python

# -----------------------------------------------------------------------
# pair.py
# -----------------------------------------------------------------------

from sys import argv
import flask
from flask import request, make_response, redirect, url_for, jsonify
from flask import render_template, flash, abort
from flask_mail import Message
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from itsdangerous import SignatureExpired
from CASClient import CASClient
from werkzeug.security import generate_password_hash, check_password_hash
from database import students, alumni, admins, groups, matches
from stable_marriage import *
from config import app, mail, s, db, login_manager
from forms import LoginForm, RegisterForm, AdminLoginForm, AdminRegisterForm, ForgotForm, PasswordResetForum
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
import time

# -----------------------------------------------------------------------

login_manager.login_view = 'login'

# class LoginForm(Form):
# username = StringField('Email', validators=[DataRequired()])
# password = PasswordField('Password', validators=[
# DataRequired(), Length(min=8, max=80)])


# class InfoForm(Form):
# firstname = StringField('First Name', validators=[DataRequired()])
# lastname = StringField('Lasr Name', validators=[DataRequired()])
# major = StringField('Major', validators=[DataRequired()])
# career = StringField('Career Field', validators=[DataRequired()])


@login_manager.user_loader
def user_loader(user_id):
    return alumni.query.filter_by(info_email=user_id).first()


@app.route("/student/logout")
# @login_required <- this makes it redirect to login when student logs out
def user_logout():
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
    username = CASClient().authenticate().replace('\n', '')
    return username


def route_new_student():
    # username = get_cas()
    # current = students.query.filter_by(studentid=username).first()
    # if not current:
    #     student_new()
    pass


@app.route('/<side>/new')
def user_new(side):
    username, user = verify_user(side)
    html = render_template('pages/user/new.html', user=user, side=side)
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


def verify_alum():
    if not current_user.is_authenticated:
        abort(redirect(url_for('login')))
    if not current_user.email_confirmed:
        abort(redirect(url_for('gotoemail')))
    if not current_user.info_firstname:
        abort(redirect(url_for('user_new')))
    return current_user.info_email


def verify_user(side):
    if side == 'alum':
        username = verify_alum()
        user = alumni.query.filter_by(info_email=username).first()
    else:
        username = CASClient().authenticate().replace('\n', '')
        user = students.query.filter_by(studentid=username).first()
        if not user:
            abort(redirect(url_for('user_new')))
    return username, user


@login_required
@app.route('/<side>/dashboard', methods=['POST', 'GET'])
def user_dashboard(side):
    username, user = verify_user(side)
    html = render_template('pages/user/dashboard.html',
                           side=side, user=user, username=username)
    return make_response('hey')


def update_info(is_new):
    #     create new user with all information except group info
    #     if is_new -> take to general change id function (same function will deal with change your group button)
    pass


@app.route('/<side>/information', methods=['POST'])
def user_information(side):
    username, user = verify_user(side)
    info = request.form
    # WTF IS THIS Group is auto going to 0 rn
    try:
        group_id = int(info.get('group_id'))
        admin = admins.query.filter_by(id=group_id).first()
        if not admin:
            html = render_template('pages/user/new.html', user=user, side=side,
                                   errorMsg="The group id you specified does not belong to an existing group")
            return make_response(html)
        elif admin.group_password and admin.group_password != info.get('group_password'):
            html = render_template('pages/user/new.html', user=user, side=side,
                                   errorMsg="The group password you entered is incorrect")
            return make_response(html)
    except:
        group_id = 0

    group_id = user.group_id
    if side == 'student':
        new_student = students(username, info.get('firstname'), info.get('lastname'),
                               f'{username}@princeton.edu', info.get('major'), info.get('career'), group_id=group_id)
        upsert_student(new_student)
    else:
        new_alum = alumni(info.get('firstname'), info.get('lastname'),
                          f"{info.get('email')}", info.get('major'), info.get('career'), group_id=group_id)
        upsert_alum(new_alum)
    return redirect(url_for('user_dashboard', side=side))


@app.route('/<side>/information-additional', methods=['POST'])
def user_information_additional(side):
    username, user = verify_user(side)
    for field in request.form:
        if field:
            setattr(user, field, request.form.get(field))
    db.session.commit()
    return redirect(url_for("user_dashboard", side=side))


@app.route('/<side>/matches', methods=['GET', 'POST'])
def user_matches(side, match=None):
    username, user = verify_user(side)
    is_alum = side == 'alum'
    errorMsg = ''
    successMsg = ''

    if not match:
        if is_alum:
            match = get_match_student(username)
        else:
            match = get_match_alum(username)

    if request.form.get("action") == "Confirm":
        if match is not None:
            if is_alum:
                match_item = matches.query.filter_by(
                    studentid=username).first()
            else:
                match_item = matches.query.filter_by(
                    info_email=username).first()
            match_item.contacted = True
            db.session.commit()

    contacted = False
    if match is not None:
        if is_alum:
            contacted = matches.query.filter_by(
                studentid=username).first().contacted
        else:
            contacted = matches.query.filter_by(
                info_email=username).first().contacted

    html = render_template('pages/user/matches.html', match=match,
                           username=username, user=user, side=side, contacted=contacted)

    if request.form.get("message") is not None:
        try:
            try:
                time = user.last_message
                last_time = datetime.strptime(str(time).split('.')[
                    0], '%Y-%m-%d %H:%M:%S')
            except:
                pass
            if (datetime.utcnow() - last_time).seconds / 3600 < 1:
                errorMsg = 'You may not send more than one message per hour.'
            else:
                db.engine.execute(
                    f"UPDATE {'alumni' if is_alum else 'students'} SET last_message=now() WHERE studentid='{user.info_email if is_alum else user.studentid}'")
                db.session.commit()
                group_id = user.group_id
                admin = admins.query.filter_by(id=group_id).first()
                email = admin.username + "@princeton.edu"

                message = request.form.get("message")
                msg = Message(
                    f'TigerPair {side.upper()} Message', sender='tigerpaircontact@gmail.com', recipients=[email])
                msg.body = message + \
                    f"\n --- \nThis message was sent to you from the {side}: " + username
                mail.send(msg)
                successMsg = 'Message successfully sent!'
        except Exception as e:
            pass
        html = render_template('pages/user/matches.html',
                               match=match, username=username, user=user, side=side,
                               contacted=contacted, successMsg=successMsg, errorMsg=errorMsg)

    return make_response(html)


@app.route('/<side>/email', methods=['GET', 'POST'])
def user_email(side):
    username, user = verify_user(side)
    errorMsg = ''
    email1 = request.form.get('email')
    email2 = request.form.get('email-repeated')
    if not email1 == email2:
        errorMsg = "Your emails must match"
    elif not verify_email_regex(request):
        errorMsg = "Please enter a valid email address"
    else:
        table = alumni if side == 'alum' else students
        if table.query.filter_by(info_email=email1).first():
            errorMsg = "That email already belongs to another account"
        else:
            user.info_email = email1
            db.session.commit()
    html = render_template('pages/user/account.html',
                           active_email=True, errorMsg=errorMsg, user=user, side=side)
    return make_response(html)


@app.route('/<side>/id', methods=['GET', 'POST'])
def user_id(side):
    username, user = verify_user(side)
    response = {}
    if request.method == "POST":
        match = matches.query.filter_by(info_email=username).first(
        ) if side == 'alum' else matches.query.filter_by(studentid=username).first()
        if match:
            response['msg'] = 'You may not change groups while you are matched'
        else:
            new_id = request.form.get('id').strip()
            if new_id:
                group = admins.query.filter_by(id=new_id).first()
                if not group:
                    response['msg'] = 'The chosen group id does not belong to an existing group'
                elif group.group_password and group.group_password != request.form.get('password'):
                    response['msg'] = 'The group password you entered is incorrect'
                else:
                    current.group_id = new_id
                    db.session.commit()
                    response['changed'] = True
                    response['id'] = new_id
                    response['msg'] = 'Success changing your group!'
    else:
        response['msg'] = 'An unexpected error occurred'
    return jsonify(response)


@app.route('/<side>/account', methods=['GET'])
def user_account(side):
    username, user = verify_user(side)
    html = render_template('pages/user/account.html',
                           active_email=True, username=username, user=user, side=side)
    return make_response(html)


@app.route('/<side>/delete', methods=['GET'])
def user_delete(side):
    username, user = verify_user(side)
    alum = get_match_student(username=username)
    if alum is not None:
        alum.matched -= 1
        matches.query.filter_by(studentid=username).delete()
    students.query.filter_by(studentid=username).delete()
    db.session.commit()
    return redirect(url_for("confirm_delete"))


def get_match_student(username):
    match = matches.query.filter_by(studentid=username).first()
    if not match:
        return None
    return alumni.query.filter_by(info_email=match.info_email).first()
# -----------------------------------------------------------------------


def verify_email_regex(request):
    email1 = request.form.get('email')
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    return search(regex, email1)


# NEW ALUM END
# -----------------------------------------------------------------------

@app.route('/resend_email', methods=['GET', 'POST'])
def resend_email():
    error = ""
    form = ForgotForm()
    if form.validate_on_submit():
        email = form.email.data
        user = alumni.query.filter_by(info_email=email).first()
        if user is not None:

            token = s.dumps(email, salt='email-confirm')

            msg = Message(
                'Confirm Email', sender='tigerpaircontact@gmail.com', recipients=[email])
            link = url_for('confirm_email', token=token, _external=True)
            msg.body = 'Click here to verify email {}'.format(link)
            mail.send(msg)
            return redirect(url_for('gotoemail'))

        else:
            error = "Invalid credentials"

    html = render_template(
        'pages/login/resend_email.html', form=form, errors=[error])  # MAKE THIS
    return make_response(html)


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
    user = alumni.query.filter_by(info_email=email).first_or_404()
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
    html = render_template('pages/visitor/index.html', side="landing")
    return make_response(html)


@app.route('/team', methods=['GET'])
def team():
    return render_template('pages/visitor/team.html')


@app.route('/admin-info', methods=['GET'])
def admininfo():
    return render_template('pages/visitor/admininfo.html')

# -----------------------------------------------------------------------
# Dynamic page function for sign in page of site
@app.route('/signin', methods=['GET'])
def matching():
    html = render_template('pages/signin/index.html')
    return make_response(html)


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = ""
    # print("login")
    if current_user.is_authenticated:
        return redirect(url_for('alumni_info'))

    form = LoginForm()
    if form.validate_on_submit():
        # print("submitted form")
        user = alumni.query.filter_by(info_email=form.email.data).first()
        if user is not None:
            # print("user is not none")
            if user.email_confirmed:
                # print("email is confirmed")
                if check_password_hash(user.password, form.password.data):
                    # print("password is correct")
                    print("this is a problem")
                    db.session.commit()
                    login_user(user, remember=form.remember.data)
                    return redirect(url_for('alumni_info'))
                else:
                    error = "Invalid email or password"
                    print("should be here")
                    # url_for('alum_info')
            else:
                error = "email not verified"
        else:
            print("invalid email")
            error = "Invalid email or password"
            print(error)

    html = render_template('pages/login/login.html', form=form, errors=[error])
    return make_response(html)

# -----------------------------------------------------------------------

# THIS IS NEW !!!!!!!
@app.route('/pages/login/update', methods=['GET', 'POST'])
def update():
    error = ""
    form = ForgotForm()
    if form.validate_on_submit():
        email = form.email.data
        user = alumni.query.filter_by(info_email=email).first()
        if user is not None:

            token = s.dumps(email, salt='password-update')

            msg = Message(
                'Update Password', sender='tigerpaircontact@gmail.com', recipients=[email])
            link = url_for('update_password', token=token, _external=True)
            msg.body = 'Click here to update password {}'.format(link)
            mail.send(msg)
            return redirect(url_for('gotoemail'))

        else:
            error = "Invalid credentials"

    html = render_template(
        'pages/login/email_update.html', form=form, errors=[error])  # MAKE THIS
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
        user = alumni.query.filter_by(info_email=email).first_or_404()
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
    error = ""
    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data
        # username = form.username.data
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        existing_user = alumni.query.filter_by(info_email=email).first()
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

        error = 'Invalid'

    html = render_template('pages/login/signup.html',
                           form=form, errors=[error])
    return make_response(html)

# -----------------------------------------------------------------------


def verify_admin(username):
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('adminlogin'))
    id = user.id
    return user.id


@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('adminlogin'))
    id = user.id
    match_list = matches.query.filter_by(group_id=id).all()
    html = render_template('pages/admin/dashboard.html',
                           matches=match_list, username=username, id=id)
    return make_response(html)

# -----------------------------------------------------------------------
# Dynamic page function for admin home page of site
@app.route('/admin/dashboard/create', methods=['GET', 'POST'])
def admin_dashboard_create():
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('adminlogin'))
    id = user.id
    create_new_matches(id)
    return redirect(url_for('admin_dashboard'))
# -----------------------------------------------------------------------

# Notify when a match has been made
@app.route('/admin/dashboard/notify', methods=['GET', 'POST'])
def notify():
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('adminlogin'))
    id = user.id
    matches = get_matches(id)
    student_emails = []
    alum_emails = []
    for match in matches:
        student = students_table.query.filter_by(
            studentid=match[0]).first().info_email
        student_emails.append(student)
        alum_emails.append(match[1])
    student_msg = Message('You\'ve been Matched!',
                          sender='tigerpaircontact@gmail.com', bcc=student_emails)
    student_msg.body = 'You have been assigned a match!\nPlease reach out to them as soon as possible to confirm your pairing. If you do not reach out within 10 days your match will be removed and reassigned to another alum.\n\nBest,\nTigerPair Team'
    mail.send(student_msg)

    alum_msg = Message('You\'ve been Matched!',
                       sender='tigerpaircontact@gmail.com', bcc=alum_emails)
    alum_msg.body = 'You have been assigned a match!\nLook out for an email from them in coming days. If they do not reach out let admin know, and you can be reassigned. Thank you for participating in this program.\n\nBest,\nTigerPair Team'
    mail.send(alum_msg)
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/modify-matches', methods=['GET'])
def admin_dashboard_modify_matches():
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('adminlogin'))
    id = user.id
    html = render_template('pages/admin/modify-matches.html',
                           matches=matches, username=username, id=id)
    return make_response(html)


@app.route('/admin/dashboard/clearall', methods=['GET', 'POST'])
def admin_dashboard_clearall():
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('adminlogin'))
    id = user.id
    clear_matches(id)
    return redirect(url_for('admin_dashboard'))

# -----------------------------------------------------------------------
@app.route('/admin/dashboard/clearone', methods=['GET', 'POST'])
def admin_dashboard_clearone():
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('adminlogin'))
    id = user.id
    clear_match(request.args.get('student'), request.args.get('alum'))
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/manual-match', methods=['GET', 'POST'])
def admin_dashboard_manual_match():
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('adminlogin'))
    id = user.id
    alumni = get_unmatched_alumni(id)
    students = get_unmatched_students(id)
    html = render_template('pages/admin/manual-match.html',
                           alumni=alumni, students=students, username=username, id=id)
    return make_response(html)


@app.route('/admin/dashboard/createone', methods=['POST', 'GET'])
def admin_dashboard_createone():
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('adminlogin'))
    id = user.id
    create_one(id, request.form.get('student'), request.form.get('alum'))
    return redirect(url_for('admin_dashboard'))


# @app.route('/admin/profiles-alum')
# def admin_profiles_alum():
#     username = get_cas()
#     user = admins.query.filter_by(username=username).first()
#     if user is None:
#         return redirect(url_for('adminlogin'))
#     id = user.id
#     alumni = get_alumni(id)
#     html = render_template('pages/admin/profiles-alum.html', alumni=alumni,
#                            side='admin', username=username, id=id)
#     return make_response(html)

# SINGLE alum profile page
# @login_required
@app.route('/admin/profile/<side>')
def admin_profile(side):
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('adminlogin'))
    id = user.id
    # side = request.args.get('side')
    if side == 'alum':
        user, match_list = get_alum(request.args.get('username'))
    else:
        user = students.query.filter_by(
            studentid=request.args.get('username')).first()
        match_list = matches.query.filter_by(
            studentid=request.args.get('username')).all()
    html = render_template('pages/admin/profile.html', matches=match_list, user=user,
                           side=side, username=username, id=id)
    return make_response(html)


# @login_required
@app.route('/admin/profiles/<side>')
def admin_profiles(side):
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('adminlogin'))
    id = user.id
    if side == 'alum':
        users = get_alumni(id)
    else:
        users = get_students(id)
    html = render_template(
        'pages/admin/profiles.html', users=users,
        side=side, username=username, id=id)
    return make_response(html)

# # SINGLE student profile page
# @login_required
# @app.route('/admin/profile-student')
# def admin_profile_student():
#     username = get_cas()
#     user = admins.query.filter_by(username=username).first()
#     if user is None:
#         return redirect(url_for('adminlogin'))
#     id = user.id
#     student, matches = get_student(request.args['username'])
#     html = render_template('pages/admin/profile.html',
#                            user=student, matches=matches,
#                            side='admin', username=username, id=id)
#     return make_response(html)


@login_required
@app.route('/admin/get-registrations/<side>', methods=['GET'])
def admin_get_registrations(side):
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('adminlogin'))
    id = user.id
    table = 'alumni' if side == 'alum' else 'students'
    registrations = db.engine.execute(
        f"SELECT DISTINCT (DATE(date_created)) AS unique_date, COUNT(*) AS amount FROM {table} WHERE group_id={id} GROUP BY unique_date ORDER BY unique_date ASC;")
    response = {str(row[0]): row[1] for row in registrations}
    return jsonify(response)


@login_required
@app.route('/admin/import/<side>', methods=['GET', 'POST'])
def admin_import(side):
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('adminlogin'))
    id = user.id
    if request.method == 'POST':
        return process_import(is_alumni=(side == 'alum'))
    page_suffix = 'alumni' if side == 'alum' else 'students'
    html = render_template(
        f'pages/admin/import-{page_suffix}.html', username=username, id=id)
    return make_response(html)


# @login_required
# @app.route('/admin/import-alumni', methods=['GET', 'POST'])
# def admin_import_alumni():
#     username = get_cas()
#     user = admins.query.filter_by(username=username).first()
#     if user is None:
#         return redirect(url_for('adminlogin'))
#     id = user.id
#     if request.method == 'POST':
#         return process_import(is_alumni=True)
#     html = render_template('pages/admin/import-alumni.html',
#                            side="Admin", username=username, id=id)
#     return make_response(html)


def process_import(is_alumni):
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('adminlogin'))
    id = user.id
    html = ''
    try:
        request_file = request.files.get('data_file')
        if not request_file.filename.strip():
            html = render_template('pages/admin/import-alumni.html' if is_alumni else 'pages/admin/import-students.html',
                                   errorMsg='No file uploaded', username=username, id=id)
        else:
            csv_reader = DictReader(chunk.decode() for chunk in request_file)
            if is_alumni:
                for row in csv_reader:
                    new_alum = alumni(info_firstname=row['First Name'], info_lastname=row['Last Name'],
                                      info_email=row['Email'], academics_major=row['Major'].upper(), career_field=row['Career'], group_id=id)
                    print(new_alum.group_id)
                    upsert_alum(new_alum)
            else:
                for row in csv_reader:
                    new_student = students(row['netid'], row['First Name'],
                                           row['Last Name'], row['Email'], row['Major'].upper(), row['Career'], group_id=id)
                    upsert_student(new_student)
            db.session.commit()
            html = render_template('pages/admin/import-alumni.html' if is_alumni else 'pages/admin/import-students.html',
                                   successMsg='Success processing your upload!', username=username, id=id)
    except Exception as e:
        html = render_template('pages/admin/import-alumni.html' if is_alumni else 'pages/admin/import-students.html',
                               errorMsg=f"Error processing your upload. It's possible that you are attempting to upload duplicate information. {str(e)}", username=username, id=id)
    return make_response(html)


@app.route('/admin/action/<side>', methods=["POST"])
def admin_action(side):
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('adminlogin'))
    id = user.id
    if request.form.get('action') == 'delete':
        users = request.form.get('checked-members').split(',')
        delete = delete_alum if side == 'alum' else delete_student
        for user in users:
            delete(id, user)
    return redirect(url_for('admin_profiles', side=side))


# @app.route('/admin/action-alum', methods=["POST"])
# def admin_action_alum():
#     username = get_cas()
#     user = admins.query.filter_by(username=username).first()
#     if user is None:
#         return redirect(url_for('adminlogin'))
#     id = user.id
#     if request.form.get('action') == 'delete':
#         alumni = request.form.get('checked-members').split(',')
#         for alum in alumni:
#             delete_alum(id, alum)
#     return redirect(url_for('admin_profiles_alum'))


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
        table_student.info_firstname = student.info_firstname
        table_student.info_lastname = student.info_lastname
        table_student.info_email = student.info_email
        table_student.academics_major = student.academics_major
        table_student.career_field = student.career_field
        table_student.group_id = student.group_id
    else:
        db.session.add(student)
    db.session.commit()


def upsert_alum(alum):
    table_alum = alumni.query.filter_by(
        info_email=alum.info_email).first()
    if table_alum:
        table_alum.info_firstname = alum.info_firstname
        table_alum.info_lastname = alum.info_lastname
        table_alum.info_email = alum.info_email
        table_alum.academics_major = alum.academics_major
        table_alum.career_field = alum.career_field
        table_alum.group_id = alum.group_id
    else:
        db.session.add(alum)
    db.session.commit()


# ---------------------------------------------------------------------

# THIS IS WHERE THE ADMIN INTERFACE BEGINS!

# make an upsert function later -TARA

@app.route('/login/admin', methods=['POST', 'GET'])
def adminlogin():
    username = get_cas()
    if admins.query.filter_by(username=username).first():
        return redirect('admin_dashboard')
    if request.method == 'POST':
        admin = admins(username=username)
        db.session.add(admin)
        db.session.commit()
        print("heyyy")
        return redirect(url_for('admin_dashboard'))
    html = render_template('pages/login/admin.html')
    return make_response(html)


@app.route('/login/asignup', methods=['GET', 'POST'])
def asignup():
    error = ""
    form = AdminRegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        existing_user = admins.query.filter_by(username=username).first()
        if existing_user is None:

            user = admins(username, hashed_password)
            db.session.add(user)
            db.session.commit()  # this isnt doing anything

            return redirect(url_for('admin_dashboard'))

    html = render_template('pages/login/asignup.html',
                           form=form, errors=[error])
    return make_response(html)


@app.route('/admin/settings', methods=['GET'])
def admin_settings():
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    id = user.id
    html = render_template('pages/admin/settings.html',
                           username=username, id=id, user=user)
    return make_response(html)


@app.route('/admin/change-id', methods=['GET', 'POST'])
def admin_change_id():
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    id = user.id
    errorMsg = ''
    if request.method == 'POST':
        netid = request.form.get('netid')
        confirm_netid = request.form.get('confirm_netid')
        if netid == confirm_netid:
            if not admins.query.filter_by(username=netid).first():
                user.username = netid
                db.session.commit()
                return redirect(url_for('index'))
            # if admin already exists, add current alumni/students to that group
            else:
                errorMsg = 'The selected user already has an account'
        else:
            errorMsg = "The entered net id's don't match"
    html = render_template('pages/admin/settings.html',
                           errorMsg=errorMsg, username=username, id=id, user=user)
    return make_response(html)


@app.route('/admin/change-password', methods=['GET', 'POST'])
def admin_change_password():
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    id = user.id
    errorMsg = ''
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password == confirm_password:
            user.group_password = password
            db.session.commit()
        else:
            errorMsg = 'The entered passwords must match'
    html = render_template('pages/admin/settings.html',
                           errorMsg=errorMsg, username=username, id=id, user=user)
    return make_response(html)


@app.route('/delete/confirm')
def confirm_delete():
    html = render_template('pages/login/delete_confirm.html')
    return make_response(html)
# @app.route('/alum/join-group', methods=['GET', 'POST'])
# def alum_join_group():
#     if request.method == 'POST':
#         pass
#     html = render_template('pages/admin/enter_group.html', side='alum')
#     return make_response(html)


# @app.route('/<side>/join-group', methods=['GET', 'POST'])
# def user_join_group():
#     if request.method == 'POST':
#         pass
#     html = render_template('pages/admin/enter_group.html', side='student')
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
