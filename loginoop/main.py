from flask import Blueprint, render_template, request, make_response
from flask_login import login_required, current_user
from . import db
from .models import Alum, Student
from CASClient import CASClient
from stable_marriage import *
from flask_user import roles_required

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')

@main.route('/alum/dashboard', methods=['GET', 'POST'])
@login_required
def alum_dashboard():
  matched = False

  firstname = request.form.get("firstname")
  lastname = request.form.get("lastname")
  email = request.form.get("email")
  major = request.form.get("major")
  career = request.form.get("career")

  if firstname is not None:
    # TODO - if logged in, don't add data again; instead, update rows
    new_alum = Alum(firstname, lastname, email, major, career, 0)
    db.session.add(new_alum)
    db.session.commit()
    html = render_template('alum_dashboard.html', firstname=firstname,
                                   lastname=lastname, email=email, major=major.upper(),
                                   career=career.capitalize(), side="Alumni", exists=True,
                                   matched=matched)
  else:
    html = render_template('alum_dashboard.html', firstname="",
                                   lastname="", email="", major="",
                                   career="", side="Alumni", exists=True, matched=matched)
  return make_response(html)

@main.route('/student/dashboard', methods=['POST', 'GET'])
def student_dashboard():
    matched = False
    username = CASClient().authenticate()

    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    major = request.form.get("major")
    career = request.form.get("career")

    current = Student.query.filter_by(studentid=username).first()

    if firstname is None:
        if current is not None:
            html = render_template('student_dashboard.html',
                                   firstname=current.studentinfonamefirst,
                                   lastname=current.studentinfonamelast,
                                   email=current.studentinfoemail,
                                   major=current.studentacademicsmajor.upper(),
                                   career=current.studentcareerdesiredfield.capitalize(),
                                   side="Student", matched=matched, username=username)

        else:
            html = render_template('student_dashboard.html', firstname="",
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
            new_student = Student(username, firstname,
                                   lastname, email, major, career, 0)
            db.session.add(new_student)
            db.session.commit()

        html = render_template('student_dashboard.html',
                               firstname=firstname,
                               lastname=lastname,
                               email=email,
                               major=major.upper(),
                               career=career.capitalize(),
                               side="Student", matched=matched, username=username)

    return make_response(html)

@main.route('/admin/dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    matches = get_matches()
    html = render_template('admin_dashboard.html', matches=matches,
                           side='Admin')
    return make_response(html)

# Dynamic page function for admin home page of site
@main.route('/admin/dashboard/create', methods=['GET'])
@login_required
def admin_dashboard_create():
    create_new_matches()
    matches = get_matches()
    html = render_template('admin_dashboard.html', matches=matches,
                           side='Admin')
    return make_response(html)


@main.route('/admin/dashboard/clearall', methods=['GET'])
@login_required
def admin_dashboard_clearall():
    clear_matches()
    html = render_template('admin_dashboard.html',
                           matches=None, side='Admin')
    return make_response(html)


@main.route('/admin/dashboard/clearone', methods=['GET'])
@login_required
def admin_dashboard_clearone():
    clear_match(request.args.get('student'), request.args.get('alum'))
    matches = get_matches()
    html = render_template('admin_dashboard.html', matches=matches,
                           side='Admin')
    return make_response(html)


@main.route('/admin/modify-matches', methods=['GET'])
@login_required
def admin_dashboard_modify_matches():
    html = render_template('admin_modify-matches.html', side='Admin')
    return make_response(html)


@main.route('/admin/unmatched-students', methods=['GET'])
@login_required
def admin_dashboard_unmatched_students():
    unmatched_students = get_unmatched_students()
    html = render_template('admin_unmatched-students.html', unmatched_students=unmatched_students,
                           side='Admin')
    return make_response(html)


@main.route('/admin/unmatched-alumni', methods=['GET'])
@login_required
def admin_dashboard_unmatched_alumni():
    unmatched_alumni = get_unmatched_alumni()
    html = render_template('admin_unmatched-alumni.html', unmatched_alumni=unmatched_alumni,
                           side='Admin')
    return make_response(html)


@main.route('/admin/match-statistics', methods=['GET'])
@login_required
def admin_dashboard_match_statistics():
    html = render_template('admin_match-statistics.html', side='Admin')
    return make_response(html)