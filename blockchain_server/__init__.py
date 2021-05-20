from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db =SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blockchain_test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    from blockchain_server import views
    
    with app.app_context():
        app.register_blueprint(views.bp)

    
    return app
