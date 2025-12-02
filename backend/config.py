import os
from urllib.parse import quote_plus

class Config:
    username = quote_plus('aadityauniyal22_db_user')
    password = quote_plus('3vQYBshs_!nv@j9')
    MONGO_URI = os.getenv('MONGO_URI', f'mongodb+srv://{username}:{password}@cluster1.4irifqj.mongodb.net/?appName=Cluster1')
    DB_NAME = 'movielens_db'
    
    DATA_DIR = '../'
    MOVIES_FILE = 'movies.csv'
    RATINGS_FILE = 'ratings.csv'
    TAGS_FILE = 'tags.csv'
    LINKS_FILE = 'links.csv'
    
    MIN_RATINGS_PER_USER = 5
    MIN_RATINGS_PER_MOVIE = 10
    N_RECOMMENDATIONS = 10
    
    ITEMS_PER_PAGE = 20
    MAX_SEARCH_RESULTS = 50
    
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    
    CACHE_TTL = 300
    ENABLE_CACHE = True
    
    # ML Model Storage Configuration
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_STORAGE_ROOT = os.path.join(BASE_DIR, 'models')
    MODEL_MATRIX_FACTORIZATION_PATH = os.path.join(MODEL_STORAGE_ROOT, 'matrix_factorization')
    MODEL_NEURAL_CF_PATH = os.path.join(MODEL_STORAGE_ROOT, 'neural_cf')
    MODEL_EMBEDDINGS_PATH = os.path.join(MODEL_STORAGE_ROOT, 'embeddings')
    
    # ML Logging Configuration
    LOG_ROOT = os.path.join(BASE_DIR, 'logs')
    ML_LOG_PATH = os.path.join(LOG_ROOT, 'ml')
    
    # ML Model Retention Policy
    MAX_MODEL_VERSIONS = 10  # Keep last 10 versions per model type
    MODEL_RETENTION_DAYS = 30  # Delete models older than 30 days
    
    # ML Training Configuration
    ML_TRAINING_SCHEDULE_ENABLED = os.getenv('ML_TRAINING_SCHEDULE_ENABLED', 'true').lower() == 'true'
    ML_TRAINING_DAY = int(os.getenv('ML_TRAINING_DAY', '6'))  # Sunday = 6
    ML_TRAINING_HOUR = int(os.getenv('ML_TRAINING_HOUR', '2'))  # 2 AM
    ML_TRAINING_MINUTE = int(os.getenv('ML_TRAINING_MINUTE', '0'))
    
    # ML Hyperparameters (defaults)
    DEFAULT_N_FACTORS = 50
    DEFAULT_LEARNING_RATE = 0.01
    DEFAULT_REGULARIZATION = 0.02
    DEFAULT_N_EPOCHS = 20
