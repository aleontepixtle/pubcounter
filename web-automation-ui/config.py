import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis & Job Queue
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    RQ_POLL_INTERVAL = 2000  # milliseconds
    
    # Security
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME', 3600))
    )
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Application Settings
    APP_NAME = os.environ.get('APP_NAME', 'Inventory Submission Portal')
    REQUIRE_ADMIN_APPROVAL = os.environ.get('REQUIRE_ADMIN_APPROVAL', 'True') == 'True'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '')
    
    # Automation Script Path
    AUTOMATION_SCRIPT_PATH = os.environ.get(
        'AUTOMATION_SCRIPT_PATH',
        '../src/utilities/selenium-inventory-submit'
    )

    # Host path for Docker-in-Docker volume mounts (when using /var/run/docker.sock)
    # This should be the absolute path on the HOST machine, not inside containers
    AUTOMATION_SCRIPT_HOST_PATH = os.environ.get(
        'AUTOMATION_SCRIPT_HOST_PATH',
        os.environ.get('AUTOMATION_SCRIPT_PATH', '../src/utilities/selenium-inventory-submit')
    )
    
    # Discord/n8n Webhook
    N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL', '')
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'True') == 'True'
    RATELIMIT_PER_USER_PER_HOUR = int(os.environ.get('RATELIMIT_PER_USER_PER_HOUR', 5))
    
    # Domain
    DOMAIN = os.environ.get('DOMAIN', 'localhost:5000')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Set to True to see SQL queries


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Require HTTPS
    
    # Ensure critical settings are set
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
