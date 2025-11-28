import pandas as pd
import numpy as np
from config import Config
from pymongo import MongoClient
import os

class DataProcessor:
    def __init__(self, use_mongodb=True):
        self.movies = None
        self.ratings = None
        self.tags = None
        self.links = None
        self.use_mongodb = use_mongodb
        self.db = None
        
        if use_mongodb:
            try:
                client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=2000)
                client.server_info()
                self.db = client[Config.DB_NAME]
                print("✅ Connected to MongoDB")
            except Exception as e:
                print(f"⚠️  MongoDB not available, using CSV files: {e}")
                self.use_mongodb = False
        
        self.load_data()
    
    def load_data(self):
        try:
            if self.use_mongodb and self.db is not None:
                self._load_from_mongodb()
            else:
                self._load_from_csv()
            
            if 'genres_list' not in self.movies.columns:
                self.movies['genres_list'] = self.movies['genres'].str.split('|')
            
            print(f"Loaded {len(self.movies)} movies, {len(self.ratings)} ratings")
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def _load_from_mongodb(self):
        print("Loading data from MongoDB...")
        
        movies_data = list(self.db['movies'].find({}, {'_id': 0}))
        ratings_data = list(self.db['ratings'].find({}, {'_id': 0}))
        
        self.movies = pd.DataFrame(movies_data)
        self.ratings = pd.DataFrame(ratings_data)
        self.tags = pd.DataFrame()
        self.links = pd.DataFrame()
        
        print("✓ Data loaded from MongoDB (movies and ratings only)")
    
    def _load_from_csv(self):
        print("Loading data from CSV files...")
        
        self.movies = pd.read_csv(f'{Config.DATA_DIR}/{Config.MOVIES_FILE}', nrows=20000)
        self.ratings = pd.read_csv(f'{Config.DATA_DIR}/{Config.RATINGS_FILE}', nrows=20000)
        self.tags = pd.DataFrame()
        self.links = pd.DataFrame()
        
        print("✓ Data loaded from CSV (movies and ratings only)")
    
    def get_movie_stats(self):
        stats = self.ratings.groupby('movieId').agg({
            'rating': ['mean', 'count']
        }).reset_index()
        stats.columns = ['movieId', 'avg_rating', 'rating_count']
        
        movies_with_stats = self.movies.merge(stats, on='movieId', how='left')
        movies_with_stats['avg_rating'] = movies_with_stats['avg_rating'].fillna(0)
        movies_with_stats['rating_count'] = movies_with_stats['rating_count'].fillna(0)
        
        return movies_with_stats
    
    def get_genre_distribution(self):
        genres = []
        for genre_list in self.movies['genres_list']:
            if isinstance(genre_list, list):
                genres.extend(genre_list)
        
        genre_counts = pd.Series(genres).value_counts()
        return genre_counts.to_dict()
    
    def get_top_rated_movies(self, min_ratings=50, limit=20):
        stats = self.get_movie_stats()
        top_movies = stats[stats['rating_count'] >= min_ratings].nlargest(limit, 'avg_rating')
        return top_movies.to_dict('records')
    
    def search_movies(self, query, limit=50):
        query = query.lower()
        results = self.movies[self.movies['title'].str.lower().str.contains(query, na=False)]
        return results.head(limit).to_dict('records')
    
    def get_movies_by_genre(self, genre, limit=50):
        results = self.movies[self.movies['genres'].str.contains(genre, case=False, na=False)]
        return results.head(limit).to_dict('records')
    
    def get_user_rating_stats(self, user_id):
        user_ratings = self.ratings[self.ratings['userId'] == user_id]
        
        if len(user_ratings) == 0:
            return None
        
        return {
            'total_ratings': len(user_ratings),
            'avg_rating': float(user_ratings['rating'].mean()),
            'favorite_genres': self._get_user_favorite_genres(user_id)
        }
    
    def _get_user_favorite_genres(self, user_id, top_n=5):
        user_ratings = self.ratings[self.ratings['userId'] == user_id]
        rated_movies = self.movies[self.movies['movieId'].isin(user_ratings['movieId'])]
        
        genre_ratings = {}
        for _, row in rated_movies.iterrows():
            rating = user_ratings[user_ratings['movieId'] == row['movieId']]['rating'].values[0]
            for genre in row['genres_list']:
                if genre not in genre_ratings:
                    genre_ratings[genre] = []
                genre_ratings[genre].append(rating)
        
        avg_genre_ratings = {genre: np.mean(ratings) for genre, ratings in genre_ratings.items()}
        sorted_genres = sorted(avg_genre_ratings.items(), key=lambda x: x[1], reverse=True)
        
        return [genre for genre, _ in sorted_genres[:top_n]]
