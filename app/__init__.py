from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import config
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Create upload folder if it doesn't exist
    import os
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Initialize scheduler for credit reset
    if not app.config['TESTING']:  # Don't run scheduler during tests
        from app.scheduler import init_scheduler
        scheduler = BackgroundScheduler()
        init_scheduler(scheduler)
        scheduler.start()
        app.scheduler = scheduler  # Store scheduler instance on app

    # Load user
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    return app 