from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class UserManager:
    def __init__(self, db):
        self.db = db
        self.users_collection = db['users'] if db is not None else None
        self.preferences_collection = db['user_preferences'] if db is not None else None
        self.favorites_collection = db['favorites'] if db is not None else None
    
    def create_user(self, username, email, password):
        if self.users_collection is None:
            return None
        
        if self.users_collection.find_one({'$or': [{'username': username}, {'email': email}]}):
            return None
        
        user = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'created_at': datetime.now(),
            'last_login': None
        }
        
        result = self.users_collection.insert_one(user)
        return str(result.inserted_id)
    
    def authenticate_user(self, username, password):
        if self.users_collection is None:
            return None
        
        user = self.users_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            self.users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {'last_login': datetime.now()}}
            )
            return {
                'user_id': str(user['_id']),
                'username': user['username'],
                'email': user['email']
            }
        return None
    
    def save_preferences(self, user_id, preferred_genres, favorite_tags):
        if self.preferences_collection is None:
            return False
        
        preferences = {
            'user_id': user_id,
            'preferred_genres': preferred_genres,
            'favorite_tags': favorite_tags,
            'updated_at': datetime.now()
        }
        
        self.preferences_collection.update_one(
            {'user_id': user_id},
            {'$set': preferences},
            upsert=True
        )
        return True
    
    def get_preferences(self, user_id):
        if self.preferences_collection is None:
            return None
        
        return self.preferences_collection.find_one({'user_id': user_id})
    
    def add_favorite(self, user_id, movie_id):
        if self.favorites_collection is None:
            return False
        
        existing = self.favorites_collection.find_one({
            'user_id': user_id,
            'movie_id': movie_id
        })
        
        if existing:
            return False
        
        favorite = {
            'user_id': user_id,
            'movie_id': movie_id,
            'added_at': datetime.now()
        }
        
        self.favorites_collection.insert_one(favorite)
        return True
    
    def remove_favorite(self, user_id, movie_id):
        if self.favorites_collection is None:
            return False
        
        result = self.favorites_collection.delete_one({
            'user_id': user_id,
            'movie_id': movie_id
        })
        return result.deleted_count > 0
    
    def get_favorites(self, user_id):
        if self.favorites_collection is None:
            return []
        
        favorites = list(self.favorites_collection.find({'user_id': user_id}))
        return [{'movie_id': fav['movie_id'], 'added_at': fav['added_at']} for fav in favorites]
    
    def is_favorite(self, user_id, movie_id):
        if self.favorites_collection is None:
            return False
        
        return self.favorites_collection.find_one({
            'user_id': user_id,
            'movie_id': movie_id
        }) is not None
