import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    UPLOAD_FOLDER = 'static/uploads'
    
    # API Keys (store in .env file)
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
    
    # Model paths
    NEWS_MODEL_PATH = 'models/fake_news_detector.pkl'
    VECTORIZER_PATH = 'models/vectorizer.pkl'
    DEEPFAKE_MODEL_PATH = 'models/deepfake_detector.h5'
    
    # Detection thresholds
    FAKE_NEWS_THRESHOLD = 0.7
    DEEPFAKE_THRESHOLD = 0.6
    
    # CORS settings
    CORS_HEADERS = 'Content-Type'
    
    # Rate limiting (optional)
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"