#!/usr/bin/env python

# -----------------------------------------------------------------------
# pair.py
# -----------------------------------------------------------------------

from sys import argv
from flask import request, make_response, redirect, url_for
from flask import render_template
from database import students, alumni, matches
from stable_marriage import get_matches, create_new_matches, clear_matches, clear_match
import yaml
from flask_mail import Message
from itsdangerous import SignatureExpired
from CASClient import CASClient
from config import app, mail, s, db

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

        if current is not None:  # Update row if student is not new
            current.studentinfonamefirst = firstname
            current.studentinfonamelast = lastname
            current.studentinfoemail = email
            current.studentacademicsmajor = major
            current.studentcareerdesiredfield = career
            db.session.commit()
        else:  # Otherwise, add new row
            new_student = students(username, firstname,
                                   lastname, email, major, career, 0)
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
def alumni_info():
    html = ''

    # PUT SOME QUERY HERE THAT DETERMINES IF USER HAS VERIFIED THEIR EMAIL

    verified = True
    if verified == False:
        html = render_template(
            '/site/pages/alumni/index.html', side="Alumni", exists=False)

        # allow email to be submitted
        # get the email from the page
        email = request.form.get("email")
        if email is not None:
            token = s.dumps(email)

            msg = Message(
                'Confirm Email', sender='tigerpaircontact@gmail.com', recipients=[email])
            link = url_for('confirm_email', token=token, _external=True)
            msg.body = 'Confirmation link is {}'.format(link)
            mail.send(msg)

    else:
        matched = False

        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        major = request.form.get("major")
        career = request.form.get("career")

        if firstname is not None:
            # TODO - if logged in, don't add data again; instead, update rows
            new_alum = alumni(firstname, lastname, email, major, career, 0)
            db.session.add(new_alum)
            db.session.commit()
            html = render_template('/site/pages/alumni/index.html', firstname=firstname,
                                   lastname=lastname, email=email, major=major.upper(),
                                   career=career.capitalize(), side="Alumni", exists=True,
                                   matched=matched)
        else:
            html = render_template('/site/pages/alumni/index.html', firstname="",
                                   lastname="", email="", major="",
                                   career="", side="Alumni", exists=True, matched=matched)
    return make_response(html)


@app.route('/confirm_email/<token>')
def confirm_email(token):

    html = ''
    errormsg = ''
    try:
        email = s.loads(token, max_age=3600)  # one hour to confirm
    except SignatureExpired:
        errormsg = 'The token is expired'

    # in the database we should have a confirmed email = false. When
    # we get here we should make confirmed = True

    html = render_template(
        '/site/pages/alumni/confirm_email', errormsg=errormsg)


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

# -----------------------------------------------------------------------
@app.route('/site/pages/admin/signin', methods=['GET'])
def admin_signin():
    html = render_template('/site/pages/admin/signin.html', side='Admin')
    return make_response(html)


@app.route('/site/pages/admin/register', methods=['GET'])
def admin_register():
    html = render_template('/site/pages/admin/register.html', side='Admin')
    return make_response(html)


@app.route('/site/pages/admin/landing', methods=['GET'])
def admin_landing():
    matches, unmatched_alumni, unmatched_students = get_matches()
    html = render_template('/site/pages/admin/landing.html', matches=matches,
                           unmatched_alumni=unmatched_alumni,
                           unmatched_students=unmatched_students,
                           side='Admin')
    return make_response(html)

# Dynamic page function for admin home page of site
@app.route('/site/pages/admin/landing/run', methods=['GET'])
def admin_landing_run():
    create_new_matches()
    matches, unmatched_alumni, unmatched_students = get_matches()
    print("CORONATIME", matches)
    html = render_template('/site/pages/admin/landing.html', matches=matches,
                           unmatched_alumni=unmatched_alumni,
                           unmatched_students=unmatched_students,
                           side='Admin')
    return make_response(html)


@app.route('/site/pages/admin/landing/clearall', methods=['GET'])
def admin_landing_clearall():
    clear_matches()
    matches, unmatched_alumni, unmatched_students = get_matches()
    html = render_template('/site/pages/admin/landing.html', matches=None,
                           unmatched_alumni=unmatched_alumni, unmatched_students=unmatched_students, side='Admin')
    return make_response(html)


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


# Runserver client, input port/host server. Returns current request,
#  and site page. As well as what GET/POST request is sent
if __name__ == '__main__':
    if len(argv) != 2:
        print('Usage: ' + argv[0] + ' port')
        exit(1)
    app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
    # db = Database(app)
