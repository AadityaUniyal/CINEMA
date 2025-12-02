import numpy as np
import pandas as pd
from scipy.sparse.linalg import svds
from sklearn.metrics import mean_squared_error
from ml.ml_logger import get_ml_logger

logger = get_ml_logger('matrix_factorization')

class MatrixFactorizationModel:
    def __init__(self, n_factors=50, learning_rate=0.01, regularization=0.02, epochs=20):
        self.n_factors = n_factors
        self.learning_rate = learning_rate
        self.regularization = regularization
        self.epochs = epochs
        self.user_factors = None
        self.movie_factors = None
        self.user_bias = None
        self.movie_bias = None
        self.global_mean = 0
        self.user_id_map = {}
        self.movie_id_map = {}
        self.reverse_user_map = {}
        self.reverse_movie_map = {}
        
    def fit(self, ratings_df, verbose=True):
        logger.info(f"Training Matrix Factorization with {len(ratings_df)} ratings")
        
        users = ratings_df['userId'].unique()
        movies = ratings_df['movieId'].unique()
        
        self.user_id_map = {uid: idx for idx, uid in enumerate(users)}
        self.movie_id_map = {mid: idx for idx, mid in enumerate(movies)}
        self.reverse_user_map = {idx: uid for uid, idx in self.user_id_map.items()}
        self.reverse_movie_map = {idx: mid for mid, idx in self.movie_id_map.items()}
        
        n_users = len(users)
        n_movies = len(movies)
        
        user_item_matrix = np.zeros((n_users, n_movies))
        for _, row in ratings_df.iterrows():
            user_idx = self.user_id_map[row['userId']]
            movie_idx = self.movie_id_map[row['movieId']]
            user_item_matrix[user_idx, movie_idx] = row['rating']
        
        self.global_mean = ratings_df['rating'].mean()
        
        self.user_factors = np.random.normal(0, 0.1, (n_users, self.n_factors))
        self.movie_factors = np.random.normal(0, 0.1, (n_movies, self.n_factors))
        self.user_bias = np.zeros(n_users)
        self.movie_bias = np.zeros(n_movies)
        
        training_history = {'epoch': [], 'rmse': []}
        
        for epoch in range(self.epochs):
            for _, row in ratings_df.iterrows():
                user_idx = self.user_id_map[row['userId']]
                movie_idx = self.movie_id_map[row['movieId']]
                rating = row['rating']
                
                prediction = self._predict_internal(user_idx, movie_idx)
                error = rating - prediction
                
                self.user_bias[user_idx] += self.learning_rate * (error - self.regularization * self.user_bias[user_idx])
                self.movie_bias[movie_idx] += self.learning_rate * (error - self.regularization * self.movie_bias[movie_idx])
                
                user_factor_update = self.learning_rate * (error * self.movie_factors[movie_idx] - self.regularization * self.user_factors[user_idx])
                movie_factor_update = self.learning_rate * (error * self.user_factors[user_idx] - self.regularization * self.movie_factors[movie_idx])
                
                self.user_factors[user_idx] += user_factor_update
                self.movie_factors[movie_idx] += movie_factor_update
            
            if verbose and (epoch + 1) % 5 == 0:
                predictions = []
                actuals = []
                for _, row in ratings_df.iterrows():
                    user_idx = self.user_id_map[row['userId']]
                    movie_idx = self.movie_id_map[row['movieId']]
                    predictions.append(self._predict_internal(user_idx, movie_idx))
                    actuals.append(row['rating'])
                
                rmse = np.sqrt(mean_squared_error(actuals, predictions))
                training_history['epoch'].append(epoch + 1)
                training_history['rmse'].append(rmse)
                logger.info(f"Epoch {epoch + 1}/{self.epochs} - RMSE: {rmse:.4f}")
        
        logger.info("Training completed")
        return training_history
    
    def _predict_internal(self, user_idx, movie_idx):
        prediction = self.global_mean + self.user_bias[user_idx] + self.movie_bias[movie_idx]
        prediction += np.dot(self.user_factors[user_idx], self.movie_factors[movie_idx])
        return np.clip(prediction, 0.5, 5.0)
    
    def predict(self, user_id, movie_id):
        if user_id not in self.user_id_map or movie_id not in self.movie_id_map:
            return self.global_mean
        
        user_idx = self.user_id_map[user_id]
        movie_idx = self.movie_id_map[movie_id]
        return self._predict_internal(user_idx, movie_idx)
    
    def recommend(self, user_id, n=10, exclude_rated=True, rated_movies=None):
        if user_id not in self.user_id_map:
            return []
        
        user_idx = self.user_id_map[user_id]
        
        predictions = []
        for movie_idx in range(len(self.movie_factors)):
            movie_id = self.reverse_movie_map[movie_idx]
            
            if exclude_rated and rated_movies and movie_id in rated_movies:
                continue
            
            pred = self._predict_internal(user_idx, movie_idx)
            predictions.append((movie_id, pred))
        
        predictions.sort(key=lambda x: x[1], reverse=True)
        return [movie_id for movie_id, _ in predictions[:n]]
    
    def get_user_embedding(self, user_id):
        if user_id not in self.user_id_map:
            return None
        user_idx = self.user_id_map[user_id]
        return self.user_factors[user_idx].copy()
    
    def get_movie_embedding(self, movie_id):
        if movie_id not in self.movie_id_map:
            return None
        movie_idx = self.movie_id_map[movie_id]
        return self.movie_factors[movie_idx].copy()
