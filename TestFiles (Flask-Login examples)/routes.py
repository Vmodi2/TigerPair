"""Logged-in page routes."""
from flask import render_template, redirect, url_for
from flask_login import current_user
from flask import current_app as app
from .assets import compile_auth_assets
from flask_login import login_required, logout_user



compile_auth_assets(app)


# Blueprint Configuration
# routes_bp = Blueprint('auth_bp', __name__,
#                     template_folder='templates',
#                     static_folder='static')
# compile_auth_assets(app)

@app.route('/site/pages/login/', methods=['GET'])
@login_required
def dashboard():
    """Serve logged-in Dashboard."""
    return render_template('/site/pages/login/dashboard.html',
                           title='Flask-Login Tutorial.',
                           template='dashboard-template',
                           current_user=current_user,
                           body="You are now logged in!")

#Fix logout
@app.route("/site/pages/logout")
@login_required
def logout():
    """User log-out logic."""
    logout_user()
    return redirect(url_for('/site/pages/login/login'))