#-----------------------------------------------------------------------
# Config.py
# All setup (keys tokens etc) put here for modularity
#-----------------------------------------------------------------------



from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap

# Flask program  runnable
app = Flask(__name__, template_folder='.')

# Generated by os.urandom(16)
# Possible breakpoint
app.secret_key = b'\xcdt\x8dn\xe1\xbdW\x9d[}yJ\xfc\xa3~/'

app.config.from_pyfile('config.cfg')

mail = Mail(app)

s = URLSafeTimedSerializer('randomkey')

# SQLAlchemy database setup
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://wrmojcmmbmrgbs:1c5df5fe85929a57652b14c8793fb2162f0c1605549df090aa613d2b95da298f@ec2-3-91-112-166.compute-1.amazonaws.com:5432/dan2dlk2ptnidd"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

bootstrap = Bootstrap(app)
