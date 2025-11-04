from flask import Flask
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from flask_wtf import CSRFProtect
from redis import Redis
from rq import Queue
from config import config
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
# CSRF protection (initialized per-app)
csrf = CSRFProtect()
# Let flask-socketio auto-detect the async mode (eventlet/gevent) and
# configure a message queue (Redis) for cross-process coordination.
socketio = SocketIO(cors_allowed_origins="*")
redis_conn = None
job_queue = None


def create_app(config_name=None):
    """Application factory pattern."""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Use the top-level templates/static directories (project templates and static
    # are mounted into /app/templates and /app/static by docker-compose). The
    # default Flask behavior looks for templates relative to the package
    # directory (app/), but our compose mounts them to the project root inside
    # the container at /app. Point the app to those locations explicitly.
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent.parent / 'templates'),
        static_folder=str(Path(__file__).parent.parent / 'static')
    )
    app.config.from_object(config[config_name])
    
    # Ensure instance folder exists
    try:
        os.makedirs(os.path.join(app.instance_path), exist_ok=True)
    except OSError:
        pass
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    # Initialize SocketIO with Redis as the message queue so that
    # connections and events work correctly when running under
    # Gunicorn/eventlet or across multiple processes.
    socketio.init_app(app, message_queue=app.config.get('REDIS_URL'))
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Initialize Redis and Queue
    global redis_conn, job_queue
    redis_conn = Redis.from_url(app.config['REDIS_URL'])
    job_queue = Queue(connection=redis_conn, default_timeout=3600)
    
    # Register blueprints
    from app.auth import auth_bp
    from app.main import main_bp
    from app.jobs import jobs_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(jobs_bp)

    # Expose csrf_token() to templates for AJAX usage
    try:
        from flask_wtf.csrf import generate_csrf
        @app.context_processor
        def _csrf_token_context():
            return dict(csrf_token=generate_csrf)
    except Exception:
        # If flask_wtf isn't available for some reason, silently skip
        pass
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if none exists only when explicitly
        # enabled via configuration. This avoids accidentally creating
        # an admin account in production containers on every startup.
        if app.config.get('CREATE_DEFAULT_ADMIN', False):
            from app.models import User
            if User.query.filter_by(username='admin').first() is None:
                admin = User(
                    username='admin',
                    email=app.config.get('ADMIN_EMAIL', 'admin@example.com'),
                    is_admin=True,
                    is_approved=True
                )
                admin.set_password('admin123')  # Change this immediately!
                db.session.add(admin)
                db.session.commit()
                app.logger.warning(
                    'Default admin user created with password "admin123". '
                    'Please change this password immediately!'
                )
        else:
            app.logger.debug('Skipping default admin creation (CREATE_DEFAULT_ADMIN not set).')
    
    return app


# csrf_token context processor is registered per-app inside create_app