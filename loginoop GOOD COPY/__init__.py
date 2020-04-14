from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = b'\xcdt\x8dn\xe1\xbdW\x9d[}yJ\xfc\xa3~/'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://wrmojcmmbmrgbs:1c5df5fe85929a57652b14c8793fb2162f0c1605549df090aa613d2b95da298f@ec2-3-91-112-166.compute-1.amazonaws.com:5432/dan2dlk2ptnidd'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import Person

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return Person.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app