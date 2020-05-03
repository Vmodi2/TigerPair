# def check(func):
#     def func_wrapper(side):
#         return 'c' + func(side) + 'c'
#     return func_wrapper
from pair import strip_user, get_cas
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import request, make_response, redirect, url_for, jsonify


def verify_user(func):
    def func_wrapper(*info):
        if side == 'alum':
            @login_required
            def verify_alum():
                if not current_user.email_confirmed:
                    return redirect(url_for('gotoemail'))
                if not current_user.info_firstname:
                    user = alumni.query.filter_by(
                        info_email=current_user.info_email).first()
                func(side)
            return verify_alum
        else:
            username = get_cas()
            user = students.query.filter_by(studentid=username).first()
            return func(side, username, user)
    return func_wrapper


@verify_user
def a(side):
    return username, user


def b():
    return "bey"


print(a('student'))
