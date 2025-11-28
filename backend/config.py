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
