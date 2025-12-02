import numpy as np
import threading
from ml.ml_logger import get_ml_logger

logger = get_ml_logger('realtime_learner')

class RealtimeLearner:
    def __init__(self, model, learning_rate=0.001):
        self.model = model
        self.learning_rate = learning_rate
        self.lock = threading.Lock()
        
    def update_user_embedding(self, user_id, movie_id, rating):
        with self.lock:
            if user_id not in self.model.user_id_map or movie_id not in self.model.movie_id_map:
                logger.warning(f"Cannot update: user {user_id} or movie {movie_id} not in model")
                return None
            
            user_idx = self.model.user_id_map[user_id]
            movie_idx = self.model.movie_id_map[movie_id]
            
            prediction = self.model._predict_internal(user_idx, movie_idx)
            error = rating - prediction
            
            self.model.user_bias[user_idx] += self.learning_rate * error
            self.model.user_factors[user_idx] += self.learning_rate * error * self.model.movie_factors[movie_idx]
            
            logger.info(f"Updated user {user_id} embedding (error: {error:.4f})")
            return self.model.user_factors[user_idx].copy()
    
    def update_movie_embedding(self, movie_id, user_id, rating):
        with self.lock:
            if user_id not in self.model.user_id_map or movie_id not in self.model.movie_id_map:
                return None
            
            user_idx = self.model.user_id_map[user_id]
            movie_idx = self.model.movie_id_map[movie_id]
            
            prediction = self.model._predict_internal(user_idx, movie_idx)
            error = rating - prediction
            
            self.model.movie_bias[movie_idx] += self.learning_rate * error
            self.model.movie_factors[movie_idx] += self.learning_rate * error * self.model.user_factors[user_idx]
            
            return self.model.movie_factors[movie_idx].copy()
    
    def apply_updates(self, updates):
        for update in updates:
            user_id = update.get('user_id')
            movie_id = update.get('movie_id')
            rating = update.get('rating')
            
            if user_id and movie_id and rating:
                self.update_user_embedding(user_id, movie_id, rating)
        
        return True
