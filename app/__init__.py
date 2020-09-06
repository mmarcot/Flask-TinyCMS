from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'makes-me-oulououuua766d'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
babel = Babel(app)
login_manager = LoginManager()
login_manager.init_app(app)

from app import views, models

@babel.localeselector
def get_locale():
    return models.Configuration.get_current_language()

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)

@app.context_processor
def inject_templates():
    pages = models.Page.query.filter_by(published=True)
    config_language = models.Configuration.get_current_language()
    return {'site_pages': pages, 'config_language': config_language}

