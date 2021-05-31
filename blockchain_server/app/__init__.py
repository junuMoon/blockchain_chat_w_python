from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

migrate = Migrate()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blockchain_test3.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "asdkfjh3on3"
    
    from .main import main as main_blueprint
    
    app.register_blueprint(main_blueprint)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    
    return app
