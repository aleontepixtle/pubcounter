from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """User model for authentication."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # User status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    saved_credentials = db.relationship('SavedCredentials', backref='user', lazy=True, 
                                       cascade='all, delete-orphan')
    jobs = db.relationship('Job', backref='user', lazy=True, 
                          cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def can_submit_job(self):
        """Check if user is approved and active."""
        return self.is_active and self.is_approved
    
    def __repr__(self):
        return f'<User {self.username}>'


class SavedCredentials(db.Model):
    """Encrypted storage for user's JW.org credentials."""
    
    __tablename__ = 'saved_credentials'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Encrypted credentials
    encrypted_username = db.Column(db.Text, nullable=False)
    encrypted_password = db.Column(db.Text, nullable=False)
    encrypted_totp_secret = db.Column(db.Text, nullable=False)
    
    # Language preference
    language = db.Column(db.String(10), default='en')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<SavedCredentials for User {self.user_id}>'


class Job(db.Model):
    """Job tracking for automation submissions."""
    
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Job identification
    rq_job_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Job status: 'queued', 'running', 'completed', 'failed'
    status = db.Column(db.String(20), default='queued', nullable=False, index=True)
    
    # Progress tracking
    progress = db.Column(db.Integer, default=0)  # 0-100
    current_step = db.Column(db.String(255))
    last_publication = db.Column(db.String(255))
    
    # Results
    result = db.Column(db.Text)  # JSON string of results
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Language used for this job
    language = db.Column(db.String(10))
    
    def __repr__(self):
        return f'<Job {self.id} - {self.status}>'
    
    def to_dict(self):
        """Convert job to dictionary for JSON responses."""
        return {
            'id': self.id,
            'rq_job_id': self.rq_job_id,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'last_publication': self.last_publication,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'language': self.language
        }