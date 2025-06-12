from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(64), nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)  # Nullable for social login
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Social login fields
    google_id = db.Column(db.String(256), unique=True, nullable=True)
    profile_pic = db.Column(db.String(512), nullable=True)
    
    # Default language preference
    language = db.Column(db.String(2), default='en')
    
    # Relationships
    analyses = db.relationship('SkinAnalysis', backref='user', lazy=True,
                               foreign_keys='SkinAnalysis.user_account_id')
    
    def set_password(self, password):
        """Set the password hash"""
        if password:
            self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check if password matches"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_social_login(self):
        """Check if user was created via social login"""
        return bool(self.google_id)
    
    def __repr__(self):
        return f'<User {self.email}>'

class SkinAnalysis(db.Model):
    """Represents a skin analysis result."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), nullable=False)  # UUID string for anonymous user
    user_account_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Registered user ID
    image_path = db.Column(db.String(255), nullable=False)  # Path in storage
    image_url = db.Column(db.String(255), nullable=False)  # URL to access image
    image_hash = db.Column(db.String(64), nullable=False)  # Perceptual hash of image
    skin_age = db.Column(db.Float, nullable=False)  # Estimated skin age
    actual_age = db.Column(db.Integer, nullable=True)  # User's actual age (optional)
    _features = db.Column('features', db.Text, nullable=False)  # JSON string of detected features
    feedback = db.Column(db.Text, nullable=False)  # Personalized feedback
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def features(self):
        """Get the features as a dictionary."""
        return json.loads(self._features)
    
    @features.setter
    def features(self, value):
        """Set the features from a dictionary."""
        self._features = json.dumps(value)
    
    def __repr__(self):
        return f'<SkinAnalysis {self.id} for user {self.user_id}>'
