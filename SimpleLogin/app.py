from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

app = Flask(__name__)
app.config['SECRET_KEY'] = '\xcdt\x8dn\xe1\xbdW\x9d[}yJ\xfc\xa3~/'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://wrmojcmmbmrgbs:1c5df5fe85929a57652b14c8793fb2162f0c1605549df090aa613d2b95da298f@ec2-3-91-112-166.compute-1.amazonaws.com:5432/dan2dlk2ptnidd"
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# This is for email verification 
mail = Mail(app)
s = URLSafeTimedSerializer('randomkey') # this is probably dangerous

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    aluminfoemail = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])



# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/site/pages/login/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        name = form.get('name')
        email = form.get('email')
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        existing_user = User.query.filter_by(email=email).first()
        if existing_user is None:
       
            # email verification code

            token = s.dumps(email)

            msg = Message('Confirm Email', sender= 'tigerpaircontact@gmail.com', recipients=[email])
            link = url_for('confirm_email', token=token, _external=True)
            msg.body= 'Confirmation link is {}'.format(link)
            mail.send(msg)

            # update the database with new user info

            user = User(name=name, email=email, password=hashed_password)
            user.email_confirmed = False # Does this have to be in User()
            db.session.add(user)
            db.session.commit()  # Create new user
            # login_user(user)

            return redirect(url_for('/site/pages/login/gotoemail'), code=400)

        flash('A user already exists with that email address.')
        return redirect(url_for('/signup'))

    return render_template('signup.html', form=form) ## WE NEED TO CREATE SIGNUP.HTML

@app.route('/confirm_email/<token>')
def confirm_email(token):

    html = ''
    errormsg = ''
    try:
        email = s.loads(token, max_age=3600) #one hour to confirm
    except SignatureExpired:
        errormsg = 'The token is expired'
        abort(404)

    user = User.query.filter_by(email=email).first_or_404() # give email column indexability

    user.email_confirmed = True
    
    db.session.add(user)
    db.session.commit()

    html = render_template('/site/pages/alumni/confirm_email.html', errormsg = errormsg)
    # add a button in confirm_email that redirects them to login

    # login_user(user)  # Log in as newly created user
    # return redirect(url_for('/site/pages/alumni/index.html')) ## idk where to redirect to


@app.route('/site/pages/login', methods=['GET', 'POST'])
def login():

    # check that user is verified
    form = LoginForm()

    if form.validate_on_submit():
        user = alumni.query.filter_by(username=form.username.data).first()
        if user is not None:
            verified = True #user.email_confirmed #hope this is the right syntax
            if verified:
                if check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember.data)
                    return redirect(url_for('site/pages/alumni/index')) # where do we want to redirect here?
            else:
                flash("email not verified")

        else:
            flash("Invalid username or password")

    return render_template('login.html', form=form)

@app.route('site/pages/alumni/')
@login_required
def dashboard():
    return render_template('index.html', name=current_user.username)

@app.route('site/pages/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
