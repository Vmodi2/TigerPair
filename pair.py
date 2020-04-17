#!/usr/bin/env python

# -----------------------------------------------------------------------
# pair.py
# -----------------------------------------------------------------------

from sys import argv
from flask import request, make_response, redirect, url_for
from flask import render_template, flash
from flask_mail import Message
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from itsdangerous import SignatureExpired
from CASClient import CASClient
from werkzeug.security import generate_password_hash, check_password_hash
from database import students, alumni, matches
from stable_marriage import *
from config import app, mail, s, db, login_manager
from forms import LoginForm, RegisterForm

# -----------------------------------------------------------------------

login_manager.login_view = 'login'

# # -----------------------------------------------------------------------

# class LoginForm(FlaskForm):
#     username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
#     password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
#     remember = BooleanField('remember me')

# # -----------------------------------------------------------------------
# class RegisterForm(FlaskForm):
#     email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
#     username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
#     password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

# -----------------------------------------------------------------------
@login_manager.user_loader
def user_loader(user_id):
    return alumni.query.filter_by(aluminfoemail=user_id).first()


@app.route("/logout")
# @login_required <- this makes it redirect to login when student logs out
def logout():
    logout_user()
    # if CASClient().validate(CASClient().stripTicket()) is not None:
    # username = CASClient().authenticate()
    # if username is not None:
    #     CASClient().logout()
    # DON'T FORGET TO logout from cas as well
    return redirect(url_for("index"))

# -----------------------------------------------------------------------
# Dynamic page function for student info page call
@app.route('/student/dashboard', methods=['POST', 'GET'])
def student_info():
    username = CASClient().authenticate().replace('\n', '')
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    major = request.form.get("major")
    career = request.form.get("career")

    current = students.query.filter_by(studentid=username).first()

    attribute = 0 if current is None else current.matched

    matched = False if attribute == 0 else True
    matchfirstname = ''
    matchlastname = ''
    matchemail = ''
    if matched:
        match = matches.query.filter_by(studentid=username).first()
        matchemail = match.aluminfoemail
        match = alumni.query.filter_by(aluminfoemail=matchemail).first()
        matchfirstname = match.aluminfonamefirst
        matchlastname = match.aluminfonamelast

    if firstname is None:
        if current is not None:
            html = render_template('pages/student/dashboard.html',
                                   firstname=current.studentinfonamefirst,
                                   lastname=current.studentinfonamelast,
                                   email=current.studentinfoemail,
                                   major=current.studentacademicsmajor.upper(),
                                   career=current.studentcareerdesiredfield,
                                   side="Student", matched=matched, username=username,
                                   matchfirstname=matchfirstname,
                                   matchlastname=matchlastname,
                                   matchemail=matchemail)

        else:
            html = render_template('pages/student/dashboard.html', firstname="",
                                   lastname="", email="", major="",
                                   career="", side="Student", matched=matched,
                                   username=username,
                                   matchfirstname=matchfirstname,
                                   matchlastname=matchlastname,
                                   matchemail=matchemail)
    else:

        if current is not None:  # Update row if student is not new
            current.studentinfonamefirst = firstname
            current.studentinfonamelast = lastname
            current.studentinfoemail = email
            current.studentacademicsmajor = major.upper()
            current.studentcareerdesiredfield = career
            db.session.commit()
        else:  # Otherwise, add new row
            new_student = students(username, firstname,
                                   lastname, email, major.upper(), career, 0)
            db.session.add(new_student)
            db.session.commit()

        html = render_template('pages/student/dashboard.html',
                               firstname=firstname,
                               lastname=lastname,
                               email=email,
                               major=major.upper(),
                               career=career,
                               side="Student", matched=matched,
                               username=username,
                               matchfirstname=matchfirstname,
                               matchlastname=matchlastname,
                               matchemail=matchemail)

    return make_response(html)

# -----------------------------------------------------------------------


@app.route('/alum/dashboard', methods=['POST', 'GET'])
@login_required
def alumni_info():
    html = ''

    if current_user.email_confirmed:

        # THIS ASSUMES THERE IS ONLY ONE MATCH FOR EACH ALUM. THIS WILL
        # FAIL OTHERWISE.
        matched = False if current_user.matched == 0 else True
        matchfirstname = ''
        matchlastname = ''
        matchemail = ''
        if matched:
            match = matches.query.filter_by(
                aluminfoemail=current_user.aluminfoemail).first()
            match = students.query.filter_by(studentid=match.studentid).first()
            matchfirstname = match.studentinfonamefirst
            matchlastname = match.studentinfonamelast
            matchemail = match.studentinfoemail

        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        major = request.form.get("major")
        career = request.form.get("career")

        if firstname is not None:
            current_user.aluminfonamefirst = firstname
            current_user.aluminfonamelast = lastname
            current_user.alumacademicsmajor = major.upper()
            current_user.alumcareerfield = career
            db.session.commit()
            html = render_template('pages/alum/dashboard.html', firstname=firstname,
                                   lastname=lastname, email=email, major=major.upper(),
                                   career=career, side="Alumni", matched=matched,
                                   matchfirstname=matchfirstname,
                                   matchlastname=matchlastname,
                                   matchemail=matchemail)
        else:
            firstname = current_user.aluminfonamefirst
            firstname = "" if firstname is None else firstname
            lastname = current_user.aluminfonamelast
            lastname = "" if lastname is None else lastname
            email = current_user.aluminfoemail
            email = "" if email is None else email
            major = current_user.alumacademicsmajor
            major = "" if major is None else major.upper()
            career = current_user.alumcareerfield
            career = "" if career is None else career

            html = render_template('pages/alum/dashboard.html', firstname=firstname,
                                   lastname=lastname, email=email, major=major,
                                   career=career, side="Alumni", matched=matched,
                                   matchfirstname=matchfirstname,
                                   matchlastname=matchlastname,
                                   matchemail=matchemail)
    else:
        return redirect(url_for('login'))

    return make_response(html)
# -----------------------------------------------------------------------


@app.route('/confirm_email/<token>')
def confirm_email(token):

    html = ''
    errormsg = ''
    try:
        email = s.loads(token, salt='email-confirm',
                        max_age=3600)  # one hour to confirm
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
    html = render_template('pages/index.html')
    return make_response(html)

# -----------------------------------------------------------------------
# Dynamic page function for sign in page of site
@app.route('/signin', methods=['GET'])
def matching():
    html = render_template('pages/signin/index.html')
    return make_response(html)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('alumni_info'))

    form = LoginForm()
    if form.validate_on_submit():
        user = alumni.query.filter_by(username=form.username.data).first()
        if user is not None:
            if user.email_confirmed:
                if check_password_hash(user.password, form.password.data):
                    db.session.commit()
                    login_user(user, remember=form.remember.data)
                    return redirect(url_for('alumni_info'))
            else:
                flash("email not verified")

        else:
            flash("Invalid username or password")

    html = render_template('pages/login/login.html', form=form)
    return make_response(html)

# -----------------------------------------------------------------------


@app.route('/login/gotoemail', methods=['GET', 'POST'])
def gotoemail():
    return render_template('pages/login/gotoemail.html')


@app.route('/login/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        name = form.username.data
        email = form.email.data
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

            user = alumni(None, None, email, None, None,
                          name, hashed_password, 0, False)
            db.session.add(user)
            db.session.commit()  # Create new user

            return redirect(url_for('gotoemail'), code=400)

        flash('A user already exists with that email address.')

    # WE NEED TO CREATE SIGNUP.HTML
    return render_template('pages/login/signup.html', form=form)

# -----------------------------------------------------------------------
@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    username = CASClient().authenticate()
    matches = get_matches()
    html = render_template('pages/admin/dashboard.html', matches=matches,
                           side='Admin')
    return make_response(html)
# -----------------------------------------------------------------------
# Dynamic page function for admin home page of site
@app.route('/admin/dashboard/create', methods=['GET'])
def admin_dashboard_create():
    username = CASClient().authenticate()
    create_new_matches()
    matches = get_matches()
    html = render_template('pages/admin/dashboard.html', matches=matches,
                           side='Admin')
    return make_response(html)
# -----------------------------------------------------------------------


@app.route('/admin/modify-matches', methods=['GET'])
def admin_dashboard_modify_matches():
    username = CASClient().authenticate()
    html = render_template('pages/admin/modify-matches.html', side='Admin')
    return make_response(html)


@app.route('/admin/dashboard/clearall', methods=['GET'])
def admin_dashboard_clearall():
    username = CASClient().authenticate()
    clear_matches()
    matches = None
    html = render_template('pages/admin/dashboard.html', matches=matches,
                           side='Admin')
    return make_response(html)

# -----------------------------------------------------------------------
@app.route('/admin/dashboard/clearone', methods=['GET'])
def admin_dashboard_clearone():
    username = CASClient().authenticate()
    clear_match(request.args.get('student'), request.args.get('alum'))
    matches = get_matches()
    html = render_template('pages/admin/dashboard.html', matches=matches,
                           side='Admin')
    return make_response(html)


@app.route('/admin/manual-match', methods=['GET'])
def admin_dashboard_manual_match():
    username = CASClient().authenticate()
    alumni = get_unmatched_alumni()
    students = get_unmatched_students()
    html = render_template('pages/admin/manual-match.html', alumni=alumni, students=students,
                           side='Admin')
    return make_response(html)


@app.route('/admin/dashboard/createone', methods=['POST', 'GET'])
def admin_dashboard_createone():
    username = CASClient().authenticate()
    create_one(request.form.get('student'), request.form.get('alum'))
    matches = get_matches()
    html = render_template('pages/admin/dashboard.html', matches=matches,
                           side='Admin')
    return make_response(html)


@app.route('/admin/profiles-alum')
def admin_profiles_alum():
    username = CASClient().authenticate()
    alumni = get_alumni()
    html = render_template('pages/admin/profiles-alum.html', alumni=alumni,
                           side='Admin')
    return make_response(html)

# SINGLE alum profile page
@app.route('/admin/profile-alum')
def admin_profile_alum():
    username = CASClient().authenticate()
    alum, matches = get_alum(request.args['email'])
    html = render_template('pages/admin/profile-alum.html',
                           alum=alum, matches=matches,
                           side='Admin')
    return make_response(html)


@app.route('/admin/profiles-student')
def admin_profiles_student():
    username = CASClient().authenticate()
    students = get_students()
    html = render_template(
        'pages/admin/profiles-student.html', students=students,
        side='Admin')
    return make_response(html)

# SINGLE student profile page
@app.route('/admin/profile-student')
def admin_profile_student():
    username = CASClient().authenticate()
    student, matches = get_student(request.args['netid'])
    html = render_template('pages/admin/profile-student.html',
                           student=student, matches=matches,
                           side='Admin')
    return make_response(html)


@app.route('/admin/match-statistics', methods=['GET'])
def admin_match_statistics():
    username = CASClient().authenticate()
    html = render_template('pages/admin/match-statistics.html',
                           side='Admin')
    return make_response(html)


@app.route('/admin/get-registrations', methods=['GET'])
def admin_get_registrations():
    username = CASClient().authenticate()
    registrations = db.engine.execute("SELECT DISTINCT (DATE(date_created)) AS unique_date, COUNT(*) AS amount FROM alumni GROUP BY unique_date ORDER BY unique_date ASC;")
    html = ''
    for row in registrations:
        html += str(row) + ';'
    print(html)
    response = make_response(html)
    return response


# -----------------------------------------------------------------------
# Runserver client, input port/host server. Returns current request,
#  and site page. As well as what GET/POST request is sent
if __name__ == '__main__':
    if len(argv) != 2:
        print('Usage: ' + argv[0] + ' port')
        exit(1)
    app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
    # db = Database(app)
