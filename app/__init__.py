from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail


db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'deekshantsharma36@gmail.com'  # Replace with actual email
    app.config['MAIL_PASSWORD'] = 'wqxs dnsj hyhk uutr'     # Use app password for Gmail
    app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'

    db.init_app(app)
    migrate = Migrate(app,db)
    login_manager.init_app(app)
    mail.init_app(app)
    login_manager.login_view = 'main.login'  # Route for login page

    # Import and register blueprints (routes)
    from .routes import main
    app.register_blueprint(main)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app