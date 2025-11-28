import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from config import Config

class RecommendationEngine:
    def __init__(self, data_processor):
        self.dp = data_processor
        self.user_item_matrix = None
        self.movie_similarity_matrix = None
        self.content_similarity_matrix = None
        self.build_models()
    
    def build_models(self):
        """Build recommendation models"""
        print("Building recommendation models...")
        self._build_collaborative_filtering()
        self._build_content_based()
        print("Models built successfully!")
    
    def _build_collaborative_filtering(self):
        """Build user-item matrix for collaborative filtering"""
        # Create user-item matrix
        self.user_item_matrix = self.dp.ratings.pivot_table(
            index='userId',
            columns='movieId',
            values='rating'
        ).fillna(0)
        
        # Calculate movie similarity matrix
        movie_ratings = self.user_item_matrix.T
        self.movie_similarity_matrix = cosine_similarity(movie_ratings)
    
    def _build_content_based(self):
        """Build content-based filtering using genres"""
        # Create TF-IDF matrix from genres
        tfidf = TfidfVectorizer(tokenizer=lambda x: x, lowercase=False, token_pattern=None)
        tfidf_matrix = tfidf.fit_transform(self.dp.movies['genres_list'])
        
        # Calculate content similarity
        self.content_similarity_matrix = cosine_similarity(tfidf_matrix)
    
    def get_collaborative_recommendations(self, user_id, n=10):
        """Get recommendations using collaborative filtering"""
        if user_id not in self.user_item_matrix.index:
            return []
        
        # Get user's ratings
        user_ratings = self.user_item_matrix.loc[user_id]
        rated_movies = user_ratings[user_ratings > 0].index.tolist()
        
        if len(rated_movies) == 0:
            return []
        
        # Calculate predicted ratings for unrated movies
        predictions = {}
        movie_ids = self.user_item_matrix.columns.tolist()
        movie_id_to_idx = {mid: idx for idx, mid in enumerate(movie_ids)}
        
        for movie_id in movie_ids:
            if movie_id not in rated_movies:
                movie_idx = movie_id_to_idx[movie_id]
                similar_movies = []
                
                for rated_movie in rated_movies:
                    if rated_movie in movie_id_to_idx:
                        rated_idx = movie_id_to_idx[rated_movie]
                        similarity = self.movie_similarity_matrix[movie_idx][rated_idx]
                        rating = user_ratings[rated_movie]
                        similar_movies.append((similarity, rating))
                
                if similar_movies:
                    # Weighted average
                    total_sim = sum(sim for sim, _ in similar_movies)
                    if total_sim > 0:
                        predicted_rating = sum(sim * rating for sim, rating in similar_movies) / total_sim
                        predictions[movie_id] = predicted_rating
        
        # Sort and return top N
        top_movies = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:n]
        return [int(movie_id) for movie_id, _ in top_movies]
    
    def get_content_based_recommendations(self, movie_id, n=10):
        """Get similar movies using content-based filtering"""
        movie_idx = self.dp.movies[self.dp.movies['movieId'] == movie_id].index
        
        if len(movie_idx) == 0:
            return []
        
        movie_idx = movie_idx[0]
        similarity_scores = list(enumerate(self.content_similarity_matrix[movie_idx]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N similar movies (excluding the movie itself)
        similar_indices = [i for i, _ in similarity_scores[1:n+1]]
        similar_movie_ids = self.dp.movies.iloc[similar_indices]['movieId'].tolist()
        
        return similar_movie_ids
    
    def get_hybrid_recommendations(self, user_id, n=10):
        """Get hybrid recommendations combining collaborative and content-based"""
        collab_recs = self.get_collaborative_recommendations(user_id, n * 2)
        
        if not collab_recs:
            # Fallback to popular movies
            return self._get_popular_movies(n)
        
        # Enhance with content-based diversity
        hybrid_recs = []
        seen = set()
        
        for movie_id in collab_recs:
            if movie_id not in seen:
                hybrid_recs.append(movie_id)
                seen.add(movie_id)
            
            if len(hybrid_recs) >= n:
                break
        
        return hybrid_recs[:n]
    
    def _get_popular_movies(self, n=10):
        """Get popular movies as fallback"""
        movie_stats = self.dp.ratings.groupby('movieId').agg({
            'rating': ['mean', 'count']
        }).reset_index()
        movie_stats.columns = ['movieId', 'avg_rating', 'count']
        
        # Filter movies with at least 50 ratings
        popular = movie_stats[movie_stats['count'] >= 50]
        popular = popular.nlargest(n, 'avg_rating')
        
        return popular['movieId'].tolist()
    
    def get_similar_users(self, user_id, n=5):
        """Find similar users based on rating patterns"""
        if user_id not in self.user_item_matrix.index:
            return []
        
        user_vector = self.user_item_matrix.loc[user_id].values.reshape(1, -1)
        similarities = cosine_similarity(user_vector, self.user_item_matrix.values)[0]
        
        similar_user_indices = np.argsort(similarities)[::-1][1:n+1]
        similar_user_ids = self.user_item_matrix.index[similar_user_indices].tolist()
        
        return similar_user_ids
