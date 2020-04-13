"""Routes for user authentication."""
from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask_login import login_required, current_user, login_user
from flask import current_app as app
from .assets import compile_auth_assets
from .forms import LoginForm, SignupForm
from .models import db, User
from .import login_manager
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mail import Mail, Message




# Blueprint Configuration
# auth_bp = Blueprint('auth_bp', __name__,
#                     template_folder='templates',
#                     static_folder='static')
# compile_auth_assets(app)

app.secret_key = b'\xcdt\x8dn\xe1\xbdW\x9d[}yJ\xfc\xa3~/'
mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

@app.route('/site/pages/login/signup', methods=['GET', 'POST'])
def signup():
    """
    User sign-up page.
    GET: Serve sign-up page.
    POST: If submitted credentials are valid, redirect user to the logged-in homepage.
    """
    signup_form = SignupForm()

    if request.method == 'POST':
        if signup_form.validate_on_submit():
            name = signup_form.get('name')
            email = signup_form.get('email')
            password = signup_form.get('password')
            existing_user = User.query.filter_by(email=email).first()  # Check if user exists
            if existing_user is None:
                ## allow email to be submitted
                ## get the email from the page
                
                token = s.dumps(email)

                msg = Message('Confirm Email', sender= 'tigerpaircontact@gmail.com', recipients=[email])
                link = url_for('confirm_email', token=token, _external=True)
                msg.body= 'Confirmation link is {}'.format(link)
                mail.send(msg)
                
                user = User(name=name,
                            email=email,
                            website=website)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()  # Create new user
                login_user(user)  # Log in as newly created user
                return redirect(url_for('/site/pages/login/dashboard'), code=400)
            flash('A user already exists with that email address.')
            return redirect(url_for('/site/pages/login/signup'))

    return render_template('/site/pages/login/signup.jinja2',
                           title='Create an Account.',
                           form=signup_form,
                           template='signup-page',
                           body="Sign up for a user account.",
                           link=link) #ADDED THIS - TARA

@app.route('/confirm_email/<token>')
def confirm_email(token):

    html = ''
    errormsg = ''
    try:
        email = s.loads(token, max_age=3600) #one hour to confirm
    except SignatureExpired:
        errormsg = 'The token is expired'
        abort(404)

    user = User.query.filter_by(email=email).first_or_404()

    user.email_confirmed = True
    
    db.session.add(user)
    db.session.commit()

    return redirect(url_for('signin')) ## idk where to redirect to

    # in the database we should have a confirmed email = false. When
    # we get here we should make confirmed = True



    html = render_template('/site/pages/alumni/confirm_email', errormsg = errormsg)


@app.route('/site/pages/login', methods=['GET', 'POST'])
def login():
    """
    User login page.
    GET: Serve Log-in page.
    POST: If form is valid and new user creation succeeds, redirect user to the logged-in homepage.
    """
    if current_user.is_authenticated:
        return redirect(url_for('/site/pages/login/dashboard'))  # Bypass if user is logged in

    login_form = LoginForm()
    if request.method == 'POST':
        if login_form.validate_on_submit():
            email = login_form.get('email')
            password = login_form.get('password')
            user = User.query.filter_by(email=email).first()  # Validate Login Attempt
            if user and user.check_password(password=password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('/site/pages/login/dashboard'))
        flash('Invalid username/password combination')
        return redirect(url_for('/site/pages/login/login'))

    return render_template('/site/pages/login/login.jinja2',
                           form=login_form,
                           title='Log in.',
                           template='login-page',
                           body="Log in with your User account.")


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('/site/pages/login/login')) 