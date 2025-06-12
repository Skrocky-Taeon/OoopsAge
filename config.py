import os

class Config:
    """Configuration settings for the Flask app."""
    # Flask settings
    DEBUG = True
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'myskinageappsecret')
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///myskin.db')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = '/tmp/uploads'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Image restrictions
    MIN_IMAGE_WIDTH = 300  # 최소 이미지 너비 (픽셀)
    MIN_IMAGE_HEIGHT = 300  # 최소 이미지 높이 (픽셀)
    MAX_IMAGE_WIDTH = 4000  # 최대 이미지 너비 (픽셀)
    MAX_IMAGE_HEIGHT = 4000  # 최대 이미지 높이 (픽셀)
    MIN_FILE_SIZE = 10 * 1024  # 최소 파일 크기 (10KB)
    # 이미지 업로드 가이드라인 문구
    UPLOAD_GUIDELINES = 'Upload any image - yourself, your favorite celebrity, or even a 20-year-old photo!'
    
    # API keys
    REPLICATE_API_KEY = os.environ.get('REPLICATE_API_KEY', '')
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', '')
    
    # App-specific settings
    APP_NAME = 'Ooops Age'
    APP_DESCRIPTION = 'Upload any image and playfully guess how old it looks - just for fun!'
    DEFAULT_LANGUAGE = 'en'
    
    # Firebase settings
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY', '')
    FIREBASE_AUTH_DOMAIN = os.environ.get('FIREBASE_AUTH_DOMAIN', '')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', '')
    FIREBASE_STORAGE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET', '')
    FIREBASE_MESSAGING_SENDER_ID = os.environ.get('FIREBASE_MESSAGING_SENDER_ID', '')
    FIREBASE_APP_ID = os.environ.get('FIREBASE_APP_ID', '')
