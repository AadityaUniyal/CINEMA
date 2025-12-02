import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from ml.ml_logger import get_ml_logger

logger = get_ml_logger('explainer_service')

class ExplainerService:
    def __init__(self, model, data_processor):
        self.model = model
        self.data_processor = data_processor
        
    def explain_recommendation(self, user_id, movie_id):
        reasons = []
        
        similar_movies = self.find_similar_rated_movies(user_id, movie_id, n=3)
        if similar_movies:
            reasons.append({
                'type': 'similar_movies',
                'description': 'Because you rated these movies highly',
                'movies': similar_movies
            })
        
        genre_score = self.get_genre_match_score(user_id, movie_id)
        if genre_score > 0.5:
            movie_data = self.data_processor.movies[self.data_processor.movies['movieId'] == movie_id]
            if not movie_data.empty:
                genres = movie_data.iloc[0]['genres_list']
                reasons.append({
                    'type': 'genre_match',
                    'description': 'Matches your favorite genres',
                    'genres': genres,
                    'match_score': float(genre_score)
                })
        
        similar_users_info = self.get_similar_users_influence(user_id, movie_id)
        if similar_users_info:
            reasons.append(similar_users_info)
        
        predicted_rating = self.model.predict(user_id, movie_id)
        
        movie_data = self.data_processor.movies[self.data_processor.movies['movieId'] == movie_id]
        movie_title = movie_data.iloc[0]['title'] if not movie_data.empty else f"Movie {movie_id}"
        
        explanation = {
            'movie_id': movie_id,
            'movie_title': movie_title,
            'predicted_rating': float(predicted_rating),
            'confidence': min(len(reasons) / 3.0, 1.0),
            'reasons': reasons
        }
        
        return explanation
    
    def find_similar_rated_movies(self, user_id, movie_id, n=3):
        user_ratings = self.data_processor.ratings[self.data_processor.ratings['userId'] == user_id]
        high_rated = user_ratings[user_ratings['rating'] >= 4.0]
        
        if high_rated.empty:
            return []
        
        movie_embedding = self.model.get_movie_embedding(movie_id)
        if movie_embedding is None:
            return []
        
        similarities = []
        for _, row in high_rated.iterrows():
            rated_movie_id = row['movieId']
            if rated_movie_id == movie_id:
                continue
            
            rated_embedding = self.model.get_movie_embedding(rated_movie_id)
            if rated_embedding is not None:
                sim = cosine_similarity([movie_embedding], [rated_embedding])[0][0]
                similarities.append((rated_movie_id, row['rating'], sim))
        
        similarities.sort(key=lambda x: x[2], reverse=True)
        
        similar_movies = []
        for rated_movie_id, rating, sim in similarities[:n]:
            movie_data = self.data_processor.movies[self.data_processor.movies['movieId'] == rated_movie_id]
            if not movie_data.empty:
                similar_movies.append({
                    'id': int(rated_movie_id),
                    'title': movie_data.iloc[0]['title'],
                    'your_rating': float(rating),
                    'similarity': float(sim)
                })
        
        return similar_movies
    
    def get_genre_match_score(self, user_id, movie_id):
        user_stats = self.data_processor.get_user_rating_stats(user_id)
        if not user_stats or not user_stats.get('favorite_genres'):
            return 0.0
        
        favorite_genres = set(user_stats['favorite_genres'])
        
        movie_data = self.data_processor.movies[self.data_processor.movies['movieId'] == movie_id]
        if movie_data.empty:
            return 0.0
        
        movie_genres = set(movie_data.iloc[0]['genres_list'])
        
        if not movie_genres:
            return 0.0
        
        overlap = len(favorite_genres & movie_genres)
        score = overlap / len(movie_genres)
        
        return score
    
    def get_similar_users_influence(self, user_id, movie_id):
        user_embedding = self.model.get_user_embedding(user_id)
        if user_embedding is None:
            return None
        
        movie_ratings = self.data_processor.ratings[self.data_processor.ratings['movieId'] == movie_id]
        
        if movie_ratings.empty:
            return None
        
        similar_count = 0
        total_rating = 0
        
        for _, row in movie_ratings.iterrows():
            other_user_id = row['userId']
            if other_user_id == user_id:
                continue
            
            other_embedding = self.model.get_user_embedding(other_user_id)
            if other_embedding is not None:
                sim = cosine_similarity([user_embedding], [other_embedding])[0][0]
                if sim > 0.7:
                    similar_count += 1
                    total_rating += row['rating']
        
        if similar_count == 0:
            return None
        
        avg_rating = total_rating / similar_count
        
        return {
            'type': 'similar_users',
            'description': 'Users with similar taste enjoyed this',
            'similar_user_count': similar_count,
            'avg_rating': float(avg_rating)
        }
