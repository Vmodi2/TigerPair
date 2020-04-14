from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from . import db
from flask_user import roles_required
from .models import Role

auth = Blueprint('auth', __name__)

@auth.route('/alum/login')
def alum_login():
    return render_template('alum_login.html')

@auth.route('/alum/login', methods=['POST'])
def alum_login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    
    user = Role.query.filter_by(email=email).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.alum_login')) # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.alum_dashboard'))

@auth.route('/alum/signup')
def alum_signup():
    return render_template('alum_signup.html')

@auth.route('/alum/signup', methods=['POST'])
def alum_signup_post():
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = Role.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.alum_signup'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = Role(email=email, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.alum_login'))

@auth.route('/alum_logout')
@login_required
def alum_logout():
    logout_user()
    return redirect(url_for('main.index'))

###############

@auth.route('/admin/login')
def admin_login():
    return render_template('admin_login.html')

@auth.route('/admin/login', methods=['POST'])
def admin_login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    
    user = Role.query.filter_by(email=email).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.admin_login')) # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.admin_dashboard'))

@auth.route('/admin/signup')
def admin_signup():
    return render_template('admin_signup.html')

@auth.route('/admin/signup', methods=['POST'])
def admin_signup_post():
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = Role.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.admin_signup'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = Role(email=email, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.admin_login'))

@auth.route('/admin_logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('main.index'))