"""User Authentication and Registration System"""
from pymongo import MongoClient
from config import Config
import hashlib
import secrets
import re
from datetime import datetime

class UserAuth:
    def __init__(self, db=None):
        try:
            if db is not None:
                self.db = db
            else:
                self.client = MongoClient(Config.MONGO_URI)
                self.db = self.client[Config.DB_NAME]
            self.users_collection = self.db['users']
            self.user_profiles_collection = self.db['user_profiles']
            self._create_indexes()
        except Exception as e:
            print(f"Error connecting to database: {e}")
            self.users_collection = None
            self.user_profiles_collection = None
    
    def _create_indexes(self):
        if self.users_collection is not None:
            self.users_collection.create_index('email', unique=True)
            self.users_collection.create_index('userId', unique=True)
            self.user_profiles_collection.create_index('userId', unique=True)
    
    def _generate_unique_user_id(self):
        while True:
            user_id = secrets.randbelow(90000000) + 10000000
            if not self.users_collection.find_one({'userId': user_id}):
                return user_id
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_password(self, password):
        """
        Validate password:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        return True, "Valid"
    
    def _validate_name(self, name):
        if len(name) < 2 or len(name) > 50:
            return False, "Name must be between 2 and 50 characters"
        if not re.match(r'^[a-zA-Z\s]+$', name):
            return False, "Name can only contain letters and spaces"
        return True, "Valid"
    
    def register_user(self, name, email, password):
        """
        Register a new user
        Returns: (success, message, user_id)
        """
        if self.users_collection is None:
            return False, "Database not available", None
        
        valid, msg = self._validate_name(name)
        if not valid:
            return False, msg, None
        
        if not self._validate_email(email):
            return False, "Invalid email format", None
        
        if self.users_collection.find_one({'email': email.lower()}):
            return False, "Email already registered", None
        
        valid, msg = self._validate_password(password)
        if not valid:
            return False, msg, None
        
        user_id = self._generate_unique_user_id()
        
        hashed_password = self._hash_password(password)
        
        user_doc = {
            'userId': user_id,
            'name': name.strip(),
            'email': email.lower().strip(),
            'password': hashed_password,
            'createdAt': datetime.now(),
            'lastLogin': None
        }
        
        profile_doc = {
            'userId': user_id,
            'name': name.strip(),
            'email': email.lower().strip(),
            'preferredGenres': [],
            'favoriteMovies': [],
            'ratings': [],
            'reviews': [],
            'watchlist': [],
            'totalRatings': 0,
            'avgRating': 0,
            'favoriteGenres': [],
            'createdAt': datetime.now()
        }
        
        try:
            self.users_collection.insert_one(user_doc)
            self.user_profiles_collection.insert_one(profile_doc)
            
            return True, "Registration successful", user_id
        except Exception as e:
            return False, f"Registration failed: {str(e)}", None
    
    def login_user(self, email, password):
        """
        Login user
        Returns: (success, message, user_id, user_data)
        """
        if self.users_collection is None:
            return False, "Database not available", None, None
        
        user = self.users_collection.find_one({'email': email.lower().strip()})
        
        if not user:
            return False, "Invalid email or password", None, None
        
        hashed_password = self._hash_password(password)
        if user['password'] != hashed_password:
            return False, "Invalid email or password", None, None
        
        self.users_collection.update_one(
            {'userId': user['userId']},
            {'$set': {'lastLogin': datetime.now()}}
        )
        
        profile = self.user_profiles_collection.find_one(
            {'userId': user['userId']},
            {'_id': 0}
        )
        
        user_data = {
            'userId': user['userId'],
            'name': user['name'],
            'email': user['email'],
            'profile': profile
        }
        
        return True, "Login successful", user['userId'], user_data
    
    def get_user_profile(self, user_id):
        if self.user_profiles_collection is None:
            return None
        
        return self.user_profiles_collection.find_one(
            {'userId': user_id},
            {'_id': 0}
        )
    
    def update_user_rating(self, user_id, movie_id, rating):
        if self.user_profiles_collection is None:
            return False
        
        profile = self.get_user_profile(user_id)
        if not profile:
            return False
        
        ratings = profile.get('ratings', [])
        existing_rating = next((r for r in ratings if r['movieId'] == movie_id), None)
        
        if existing_rating:
            existing_rating['rating'] = rating
            existing_rating['timestamp'] = datetime.now()
        else:
            ratings.append({
                'movieId': movie_id,
                'rating': rating,
                'timestamp': datetime.now()
            })
        
        total_ratings = len(ratings)
        avg_rating = sum(r['rating'] for r in ratings) / total_ratings if total_ratings > 0 else 0
        
        self.user_profiles_collection.update_one(
            {'userId': user_id},
            {
                '$set': {
                    'ratings': ratings,
                    'totalRatings': total_ratings,
                    'avgRating': avg_rating
                }
            }
        )
        
        return True
    
    def add_user_review(self, user_id, movie_id, rating, comment):
        if self.user_profiles_collection is None:
            return False
        
        profile = self.get_user_profile(user_id)
        if not profile:
            return False
        
        reviews = profile.get('reviews', [])
        
        existing_review = next((r for r in reviews if r['movieId'] == movie_id), None)
        
        review_data = {
            'movieId': movie_id,
            'rating': rating,
            'comment': comment,
            'timestamp': datetime.now()
        }
        
        if existing_review:
            existing_review.update(review_data)
        else:
            reviews.append(review_data)
        
        self.user_profiles_collection.update_one(
            {'userId': user_id},
            {'$set': {'reviews': reviews}}
        )
        
        self.update_user_rating(user_id, movie_id, rating)
        
        return True
    
    def add_favorite_movie(self, user_id, movie_id):
        if self.user_profiles_collection is None:
            return False
        
        self.user_profiles_collection.update_one(
            {'userId': user_id},
            {'$addToSet': {'favoriteMovies': movie_id}}
        )
        
        return True
    
    def remove_favorite_movie(self, user_id, movie_id):
        if self.user_profiles_collection is None:
            return False
        
        self.user_profiles_collection.update_one(
            {'userId': user_id},
            {'$pull': {'favoriteMovies': movie_id}}
        )
        
        return True
    
    def update_watchlist(self, user_id, watchlist):
        if self.user_profiles_collection is None:
            return False
        
        self.user_profiles_collection.update_one(
            {'userId': user_id},
            {'$set': {'watchlist': watchlist}}
        )
        
        return True
