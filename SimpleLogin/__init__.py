from flask import Flask__
from flask_sqlalchemy import SQLAlchemy

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = b'\xf9\x19\xd1\xb1\xe2\xcb\x8e\xd1\x1cF;yIe\xc2b'
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://wrmojcmmbmrgbs:1c5df5fe85929a57652b14c8793fb2162f0c1605549df090aa613d2b95da298f@ec2-3-91-112-166.compute-1.amazonaws.com:5432/dan2dlk2ptnidd"

    db.init_app(app)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app