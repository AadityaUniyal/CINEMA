import os
from urllib.parse import quote_plus

class Config:
    # MongoDB Configuration
    username = quote_plus('aadityauniyal22_db_user')
    password = quote_plus('3vQYBshs_!nv@j9')
    MONGO_URI = os.getenv('MONGO_URI', f'mongodb+srv://{username}:{password}@cluster1.4irifqj.mongodb.net/?appName=Cluster1')
    DB_NAME = 'movielens_db'
    
    # Data paths
    DATA_DIR = '../'
    MOVIES_FILE = 'movies.csv'
    RATINGS_FILE = 'ratings.csv'
    TAGS_FILE = 'tags.csv'
    LINKS_FILE = 'links.csv'
    
    # ML Configuration
    MIN_RATINGS_PER_USER = 5
    MIN_RATINGS_PER_MOVIE = 10
    N_RECOMMENDATIONS = 10
    
    # API Configuration
    ITEMS_PER_PAGE = 20
    MAX_SEARCH_RESULTS = 50
    
    # Security
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    
    # Cache Configuration
    CACHE_TTL = 300  # 5 minutes
    ENABLE_CACHE = True
