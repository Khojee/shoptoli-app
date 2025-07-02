# shoptoli/__init__.py

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from .models import db, User
from flask_babel import Babel

# Initialize extensions but don't attach to an app yet
bcrypt = Bcrypt()
babel = Babel()
login_manager = LoginManager()
login_manager.login_view = 'main.login' # Note the 'main.' prefix for the blueprint
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    
    # --- APP CONFIGURATION ---
    app.config['SECRET_KEY'] = 'a-very-secret-key-that-should-be-changed' 
    # IMPORTANT: Replace 'your_postgres_password' with your password
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234567@localhost/shoptoli'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'Asia/Tashkent'

    # --- INITIALIZE EXTENSIONS WITH THE APP ---
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app)

    # --- REGISTER BLUEPRINT (ROUTES) ---
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # --- REGISTER CUSTOM TEMPLATE FILTER ---
    from .util import format_datetime_local
    app.jinja_env.filters['localdatetime'] = format_datetime_local
    

    return app