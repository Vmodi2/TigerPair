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
from forms import LoginForm, RegisterForm, ChangeGroupForm, AdminLoginForm, AdminRegisterForm, UserDashboardForm, ForgotForm, PasswordResetForum, NewUserForm
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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('/pages/errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('pages/errors/500.html'), 500
# how to handle 502 503 504 erros?
# @app.errorhandler(502)
# def internal_error(error):
#     db.session.rollback()
#     return render_template('pages/errors/500.html'), 500


@login_manager.user_loader
def user_loader(user_id):
    return alumni.query.filter_by(info_email=user_id).first()


@app.route("/student/logout", methods=['GET', 'POST'])
# @login_required <- this makes it redirect to login when student logs out
def user_logout():
    casClient = CASClient()
    casClient.authenticate()
    casClient.logout()
    return redirect(url_for("index"))


@app.route("/alum/logout", methods=['GET', 'POST'])
@login_required
def alum_logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/admin/logout", methods=['GET', 'POST'])
def admin_logout():
    casClient = CASClient()
    # casClient.authenticate()
    casClient.logout()
    return redirect(url_for("index"))


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


def get_cas():
    return CASClient().authenticate().replace('\n', '')


def verify_alum():
    if not current_user.is_authenticated:
        abort(redirect(url_for('login')))
    if not current_user.email_confirmed:
        abort(redirect(url_for('gotoemail')))
    return current_user.info_email


def verify_user(side):
    if side == 'alum':
        username = verify_alum()
        user = alumni.query.filter_by(info_email=username).first()
        return username, user
    elif side == 'student':
        username = get_cas()
        user = students.query.filter_by(studentid=username).first()
        if not user:
            abort(redirect(url_for('user_new', side='student')))
        return username, user
    else:
        abort(404)


def route_new_user(user, side):
    if not user.info_firstname:
        abort(redirect(url_for('user_new', side=side)))


@app.route('/<side>/profile', methods=['GET', 'POST'])
def user_profile(side):
    username, user = verify_user(side)
    route_new_user(user, side)
    msg = ''
    form = UserDashboardForm()
    form2 = ChangeGroupForm()
    if form.validate_on_submit():
        msg = update_info(user, username, side, form, False)
    html = render_template('pages/user/profile.html',
                           side=side, user=user, username=username, msg=msg, user_type=side, form=form, form2=form2)
    return make_response(html)


@app.route('/<side>/new', methods=['GET', 'POST'])
def user_new(side):
    form = NewUserForm()

    if side == 'student':
        username = get_cas()
        user = students.query.filter_by(studentid=username)
    else:
        username, user = verify_user(side)
    msg = ''
    if form.validate_on_submit():
        msg = update_info(user, username, side, form, True)
        if not msg:
            return redirect(url_for('user_dashboard', side=side))
    html = render_template('pages/user/new.html', side=side, user=user,
                           username=username, msg=msg, user_type=side, form=form)
    return make_response(html)


def update_info(user, username, side, info, with_group):
    if side == 'alum':
        new_user = alumni(info_firstname=info.firstname.data, info_lastname=info.lastname.data,
                          info_email=username, academics_major=info.major.data.upper(), career_field=info.career.data)
    else:
        new_user = students(username, info.firstname.data, info.lastname.data,
                            f'{username}@princeton.edu', info.major.data, info.career.data)
    if with_group:
        try:
            group_id = int(info.group_id.data)
            admin = admins.query.filter_by(id=group_id).first()
            if not admin:
                return "The group id you specified does not belong to an existing group"
            elif admin.group_password and admin.group_password != info.group_password.data:
                return "The group password you entered is incorrect"
        except:
            group_id = 0
        new_user.group_id = group_id
    else:
        new_user.group_id = user.group_id
    upsert_user(new_user, side)
    return ''


@app.route('/<side>/information-additional', methods=['GET', 'POST'])
def user_information_additional(side):
    username, user = verify_user(side)
    route_new_user(user, side)
    form = UserDashboardForm()
    form2 = ChangeGroupForm()
    # definitely will change this to flask forms later
    errorMsg = ''
    for field in request.form:
        value = request.form.get(field)
        if field == 'class_year':
            try:
                value = int(value)
                if value > int(datetime.today().year + 8) or value < 1930:
                    raise Exception()
            except:
                errorMsg = 'Class year must be a valid graduation year'
                continue
        setattr(user, field, value)
    db.session.commit()
    html = render_template('pages/user/profile.html',
                           side=side, user=user, username=username, active='more', user_type=side, form=form, form2=form2, errorMsg=errorMsg)
    return make_response(html)


@app.route('/<side>/dashboard', methods=['GET', 'POST'])
def user_dashboard(side):
    username, user = verify_user(side)
    route_new_user(user, side)
    form2 = ChangeGroupForm()
    is_alum = side == 'alum'
    errorMsg = ''
    successMsg = ''
    match_user = None
    if is_alum:
        match = matches.query.filter_by(info_email=username).first()
        if match is not None:
            match_user = students.query.filter_by(
                studentid=match.studentid).first()
    else:
        match = matches.query.filter_by(studentid=username).first()
        if match is not None:
            match_user = alumni.query.filter_by(
                info_email=match.info_email).first()

    if request.form.get("action") == "Confirm":
        if match is not None:
            match.contacted = True
            db.session.commit()

    contacted = False if match is None else match.contacted

    html = render_template('pages/user/dashboard.html', match=match_user,
                           username=username, user=user, side=side, contacted=contacted, user_type=side, form2=form2)

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
                where_clause = f"info_email='{user.info_email}'" if is_alum else f"studentid='{user.studentid}'"
                db.engine.execute(
                    f"UPDATE {'alumni' if is_alum else 'students'} SET last_message=now() WHERE {where_clause}")
                db.session.commit()
                group_id = user.group_id
                admin = admins.query.filter_by(id=group_id).first()
                email = admin.username + "@princeton.edu"

                message = request.form.get("message")
                msg = Message(
                    f'TigerPair {side.capitalize()} Message', sender='tigerpaircontact@gmail.com', recipients=[email])
                msg.body = message + \
                    f"\n --- \nThis message was sent to you from the {side}: " + username
                mail.send(msg)
                successMsg = 'Message successfully sent!'
        except Exception as e:
            print(e)
        html = render_template('pages/user/dashboard.html',
                               match=match_user, username=username, user=user, side=side,
                               contacted=contacted, successMsg=successMsg, errorMsg=errorMsg, user_type=side, form2=form2)

    return make_response(html)


@app.route('/<side>/email', methods=['GET', 'POST'])
def user_email(side):
    username, user = verify_user(side)
    route_new_user(user, side)
    form2 = ChangeGroupForm()
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
                           active_email=True, errorMsg=errorMsg, user=user, side=side, user_type=side, form2=form2)
    return make_response(html)


@app.route('/<side>/id', methods=['GET', 'POST'])
def user_id(side):
    username, user = verify_user(side)
    route_new_user(user, side)
    form = ChangeGroupForm()
    response = {}
    if form.validate_on_submit():
        match = matches.query.filter_by(info_email=username).first(
        ) if side == 'alum' else matches.query.filter_by(studentid=username).first()
        if match:
            response['msg'] = 'You may not change groups while you are matched'
        else:
            new_id = form.new_group_id.data
            if new_id is not None:
                group = admins.query.filter_by(id=new_id).first()
                if not group:
                    response['msg'] = 'The chosen group id does not belong to an existing group'
                elif group.group_password and group.group_password != form.group_password.data:
                    response['msg'] = 'The group password you entered is incorrect'
                elif new_id == str(user.group_id):
                    response['msg'] = 'You may not switch into your own group'
                else:
                    user.group_id = new_id
                    # is_alum = side == 'alum'
                    # where_clause = f"info_email='{user.info_email}'" if is_alum else f"studentid='{user.studentid}'"
                    # db.engine.execute(f"UPDATE {'alumni' if is_alum else 'students'} SET last_message=epoch from now() WHERE {where_clause}")
                    db.session.commit()
                    response['changed'] = True
                    response['id'] = new_id
                    response['msg'] = 'Success changing your group!'
            else:
                response['msg'] = 'Please enter a valid group id'
    else:
        response['msg'] = 'An unexpected error occurred'
    return jsonify(response)


@app.route('/<side>/account', methods=['GET', 'POST'])
def user_account(side):
    username, user = verify_user(side)
    route_new_user(user, side)
    form2 = ChangeGroupForm()
    html = render_template('pages/user/account.html',
                           active_email=True, username=username, user=user, side=side, user_type=side, form2=form2)
    return make_response(html)


@app.route('/<side>/delete', methods=['GET', 'POST'])
def user_delete(side):
    username, user = verify_user(side)
    route_new_user(user, side)
    if side == 'alum':
        matches.query.filter_by(info_email=username).delete()
        alumni.query.filter_by(info_email=username).delete()
    else:
        matches.query.filter_by(studentid=username).delete()
        students.query.filter_by(studentid=username).delete()
    db.session.commit()
    return redirect(url_for("confirm_delete"))

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


@app.route('/confirm_email/<token>', methods=['GET', 'POST'])
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
@app.route('/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    html = render_template('pages/index.html', side="landing")
    return make_response(html)


@app.route('/team', methods=['GET', 'POST'])
def team():
    return render_template('pages/visitor/team.html')


@app.route('/admin-info', methods=['GET', 'POST'])
def admininfo():
    return render_template('pages/visitor/admininfo.html')

# -----------------------------------------------------------------------
# Dynamic page function for sign in page of site
@app.route('/signin', methods=['GET', 'POST'])
def matching():
    html = render_template('pages/signin/index.html')
    return make_response(html)


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = ""
    # print("login")
    if current_user.is_authenticated:
        return redirect(url_for('user_dashboard', side='alum'))

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
                    return redirect(url_for('user_dashboard', side='alum'))
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


@app.route('/login/password_changed', methods=['GET', 'POST'])
def password_changed():
    html = render_template('pages/login/password_changed.html')
    return make_response(html)

# -----------------------------------------------------------------------


@app.route('/login/gotoemail', methods=['GET', 'POST'])
def gotoemail():
    logout_user()
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

            user = alumni(info_email=email, password=hashed_password)
            upsert_user(user, side='alum')

            return redirect(url_for('gotoemail'))

        error = 'Invalid'

    html = render_template('pages/login/signup.html',
                           form=form, errors=[error])
    return make_response(html)

# -----------------------------------------------------------------------


def verify_admin():
    username = get_cas()
    user = admins.query.filter_by(username=username).first()
    if not user:
        abort(redirect(url_for('adminlogin')))
    id = user.id
    return username, user.id


@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    username, id = verify_admin()
    match_list = matches.query.filter_by(group_id=id).all()
    html = render_template('pages/admin/dashboard.html',
                           matches=match_list, username=username, id=id, user_type='admin')
    return make_response(html)

# -----------------------------------------------------------------------
# Dynamic page function for admin home page of site
@app.route('/admin/dashboard/create', methods=['GET', 'POST'])
def admin_dashboard_create():
    username, id = verify_admin()
    matches = create_new_matches(id)
    if request.args.get('notify'):
        return notify(selective=True, members=matches)
    successMsg, errorMsg = '', ''
    if matches:
        successMsg = 'Successfully created matches!'
    else:
        errorMsg = 'No matches were created.'
    html = render_template('pages/admin/modify-matches.html',
                           successMsg=successMsg, errorMsg=errorMsg, username=username, id=id, user_type='admin')
    return make_response(html)
# -----------------------------------------------------------------------

# Notify when a match has been made
@app.route('/admin/dashboard/notify', methods=['GET', 'POST'])
def notify(selective=False, members=None):
    username, id = verify_admin()
    msg = ''
    match_list = members if selective else matches.query.filter_by(
        group_id=id).all()
    if not match_list:
        errorMsg = 'There are no members to notify'
        html = render_template('pages/admin/modify-matches.html',
                               errorMsg=errorMsg, username=username, id=id, user_type='admin')
        return make_response(html)
    student_emails = []
    alum_emails = []
    for match in match_list:
        student = students_table.query.filter_by(
            studentid=match.studentid).first().info_email
        student_emails.append(student)
        alum_emails.append(match.info_email)
    student_msg = Message('You\'ve been Matched!',
                          sender='tigerpaircontact@gmail.com', bcc=student_emails)
    student_msg.body = 'You have been assigned a match!\nPlease reach out to them as soon as possible to confirm your pairing. If you do not reach out within 10 days your match will be removed and reassigned to another alum.\n\nBest,\nTigerPair Team'
    mail.send(student_msg)

    alum_msg = Message('You\'ve been Matched!',
                       sender='tigerpaircontact@gmail.com', bcc=alum_emails)
    alum_msg.body = 'You have been assigned a match!\nLook out for an email from them in coming days. If they do not reach out let admin know, and you can be reassigned. Thank you for participating in this program.\n\nBest,\nTigerPair Team'
    mail.send(alum_msg)
    successMsg = 'Email notifications successfully sent!'
    html = render_template('pages/admin/modify-matches.html',
                           successMsg=successMsg, username=username, id=id, user_type='admin')
    return make_response(html)


@app.route('/admin/modify-matches', methods=['GET', 'POST'])
def admin_dashboard_modify_matches():
    username, id = verify_admin()
    html = render_template('pages/admin/modify-matches.html',
                           matches=matches, username=username, id=id, user_type='admin')
    return make_response(html)


@app.route('/admin/dashboard/clearall', methods=['GET', 'POST'])
def admin_dashboard_clearall():
    username, id = verify_admin()
    clear_matches(id)
    html = render_template('pages/admin/modify-matches.html',
                           successMsg='All matches were cleared!', username=username, id=id, user_type='admin')
    return make_response(html)

# -----------------------------------------------------------------------
@app.route('/admin/dashboard/clearone', methods=['GET', 'POST'])
def admin_dashboard_clearone():
    username, id = verify_admin()
    clear_match(request.args.get('student'), request.args.get('alum'))
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/manual-match', methods=['GET', 'POST'])
def admin_dashboard_manual_match():
    username, id = verify_admin()
    alumni = get_unmatched_alumni(id)
    students = get_unmatched_students(id)
    html = render_template('pages/admin/manual-match.html',
                           alumni=alumni, students=students, username=username, id=id, user_type='admin')
    return make_response(html)


@app.route('/admin/dashboard/createone', methods=['GET', 'POST'])
def admin_dashboard_createone():
    username, id = verify_admin()
    create_one(id, request.form.get('student'), request.form.get('alum'))
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/profile/<side>', methods=['GET', 'POST'])
def admin_profile(side):
    username, id = verify_admin()
    if side == 'alum':
        user, match_list = get_alum(request.args.get('username'))
    else:
        user = students.query.filter_by(
            studentid=request.args.get('username')).first()
        match_list = matches.query.filter_by(
            studentid=request.args.get('username')).all()
    html = render_template('pages/admin/profile.html', matches=match_list, user=user,
                           side=side, username=username, id=id, user_type='admin')
    return make_response(html)


# @login_required
@app.route('/admin/profiles/<side>', methods=['GET', 'POST'])
def admin_profiles(side):
    username, id = verify_admin()
    if side == 'alum':
        users = get_alumni(id)
    else:
        users = get_students(id)
    html = render_template(
        'pages/admin/profiles.html', users=users,
        side=side, username=username, id=id, user_type='admin')  # side = "admin"
    return make_response(html)


@login_required
@app.route('/admin/get-registrations/<side>', methods=['GET', 'POST'])
def admin_get_registrations(side):
    username, id = verify_admin()
    table = 'alumni' if side == 'alum' else 'students'
    registrations = db.engine.execute(
        f"SELECT DISTINCT (DATE(date_created)) AS unique_date, COUNT(*) AS amount FROM {table} WHERE group_id={id} GROUP BY unique_date ORDER BY unique_date ASC;")
    response = {str(row[0]): row[1] for row in registrations}
    return jsonify(response)


@login_required
@app.route('/admin/import/<side>', methods=['GET', 'POST'])
def admin_import(side):
    username, id = verify_admin()
    if request.method == 'POST':
        return process_import(is_alumni=(side == 'alum'))
    page_suffix = 'alumni' if side == 'alum' else 'students'
    html = render_template(
        f'pages/admin/import-{page_suffix}.html', username=username, id=id, side=side, user_type='admin')
    return make_response(html)


def process_import(is_alumni):
    username, id = verify_admin()
    side = 'alum' if is_alumni else 'student'
    html = ''
    errorMsg, successMsg = '', ''
    bad_members = []
    try:
        request_file = request.files.get('data_file')
        if not request_file.filename.strip():
            html = render_template('pages/admin/import-alumni.html' if is_alumni else 'pages/admin/import-students.html',
                                   errorMsg='No .csv file uploaded', username=username, id=id, side=side, user_type='admin')
        else:
            csv_reader = DictReader(chunk.decode() for chunk in request_file)
            if is_alumni:
                for row in csv_reader:
                    new_alum = alumni(info_firstname=row['First Name'], info_lastname=row['Last Name'],
                                      info_email=row['Email'], academics_major=row['Major'].upper(), career_field=row['Career'])
                    current = alumni.query.filter_by(
                        info_email=new_alum.info_email).first()
                    if current and current.group_id != id and current.group_id != -1:
                        bad_members.append(new_alum.info_email)
                        continue
                    new_alum.group_id = id
                    upsert_user(new_alum, side)
            else:
                for row in csv_reader:
                    new_student = students(row['netid'], row['First Name'],
                                           row['Last Name'], row['Email'], row['Major'].upper(), row['Career'])
                    current = students.query.filter_by(
                        studentid=new_student.studentid).first()
                    if current and current.group_id != id and current.group_id != -1:
                        bad_members.append(new_student.studentid)
                        continue
                    new_student.group_id = id
                    upsert_user(new_student, side)
            db.session.commit()
            if bad_members:
                errorMsg = "The following members already exist in another group:"
            else:
                successMsg = 'Success processing your upload!'
            html = render_template('pages/admin/import-alumni.html' if is_alumni else 'pages/admin/import-students.html',
                                   errorMsg=errorMsg, bad_members=bad_members, successMsg=successMsg, username=username, id=id, side=side, user_type='admin')
    except Exception as e:
        html = render_template('pages/admin/import-alumni.html' if is_alumni else 'pages/admin/import-students.html',
                               errorMsg=f"Error processing your upload. It's possible that you are attempting to upload duplicate information. {str(e)}", username=username, id=id, side=side, user_type='admin')
    return make_response(html)


@app.route('/admin/action/<side>', methods=['GET', 'POST'])
def admin_action(side):
    username, id = verify_admin()
    if request.form.get('action') == 'delete':
        users = request.form.get('checked-members').split(',')
        delete = delete_alum if side == 'alum' else delete_student
        for user in users:
            delete(id, user)
    return redirect(url_for('admin_profiles', side=side))


def upsert_user(user, side):
    table_user = alumni.query.filter_by(info_email=user.info_email).first(
    ) if side == 'alum' else students.query.filter_by(studentid=user.studentid).first()
    if table_user:
        table_user.info_firstname = user.info_firstname
        table_user.info_lastname = user.info_lastname
        table_user.info_email = user.info_email
        table_user.academics_major = user.academics_major
        table_user.career_field = user.career_field
        table_user.group_id = user.group_id
    else:
        db.session.add(user)
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


@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    username, id = verify_admin()
    user = admins.query.filter_by(username=username).first()
    html = render_template('pages/admin/settings.html',
                           username=username, id=id, user=user, user_type='admin')
    return make_response(html)


@app.route('/admin/change-id', methods=['GET', 'POST'])
def admin_change_id():
    username, id = verify_admin()
    user = admins.query.filter_by(username=username).first()
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
                           errorMsg=errorMsg, username=username, user=user, id=id, user_type='admin')
    return make_response(html)


@app.route('/admin/change-password', methods=['GET', 'POST'])
def admin_change_password():
    username, id = verify_admin()
    user = admins.query.filter_by(username=username).first()
    errorMsg, successMsg = '', ''
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password == confirm_password:
            if password == user.group_password:
                errorMsg = 'You may not use your current password'
            else:
                user.group_password = password
                db.session.commit()
                successMsg = 'Password successfully changed!'
        else:
            errorMsg = 'The entered passwords must match'
    html = render_template('pages/admin/settings.html',
                           errorMsg=errorMsg, successMsg=successMsg, username=username, user=user, id=id, user_type='admin')
    return make_response(html)


@app.route('/delete/confirm', methods=['GET', 'POST'])
def confirm_delete():
    html = render_template('pages/login/delete_confirm.html')
    return make_response(html)


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
