import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from ml.ml_logger import get_ml_logger
import json
import os

logger = get_ml_logger('feature_engineer')

class FeatureEngineer:
    """
    Feature engineering pipeline for ML recommendation system.
    Extracts and normalizes user and movie features.
    """
    
    def __init__(self):
        self.user_feature_params = {}
        self.movie_feature_params = {}
        self.genre_list = []
        
    def extract_user_features(self, ratings_df: pd.DataFrame, user_id: int) -> np.ndarray:
        """
        Extract user features including rating statistics and genre preferences.
        
        Requirements: 4.1
        """
        user_ratings = ratings_df[ratings_df['userId'] == user_id]
        
        if len(user_ratings) == 0:
            # Return default features for users with no ratings
            return self._get_default_user_features()
        
        features = []
        
        # Rating statistics
        features.append(user_ratings['rating'].mean())  # avg_rating
        features.append(user_ratings['rating'].std() if len(user_ratings) > 1 else 0)  # rating_std
        features.append(len(user_ratings))  # rating_count
        features.append(user_ratings['rating'].min())  # min_rating
        features.append(user_ratings['rating'].max())  # max_rating
        
        return np.array(features)
    
    def extract_user_features_batch(self, ratings_df: pd.DataFrame, movies_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features for all users in the dataset.
        
        Requirements: 4.1
        """
        logger.info("Extracting user features for all users")
        
        user_features = []
        
        for user_id in ratings_df['userId'].unique():
            user_ratings = ratings_df[ratings_df['userId'] == user_id]
            
            # Rating statistics
            avg_rating = user_ratings['rating'].mean()
            rating_std = user_ratings['rating'].std() if len(user_ratings) > 1 else 0
            rating_count = len(user_ratings)
            min_rating = user_ratings['rating'].min()
            max_rating = user_ratings['rating'].max()
            
            # Genre preferences
            rated_movie_ids = user_ratings['movieId'].values
            rated_movies = movies_df[movies_df['movieId'].isin(rated_movie_ids)]
            genre_prefs = self._calculate_genre_preferences(user_ratings, rated_movies)
            
            user_features.append({
                'userId': user_id,
                'avg_rating': avg_rating,
                'rating_std': rating_std,
                'rating_count': rating_count,
                'min_rating': min_rating,
                'max_rating': max_rating,
                **genre_prefs
            })
        
        user_features_df = pd.DataFrame(user_features)
        
        # Store normalization parameters
        self.user_feature_params = {
            'avg_rating_mean': user_features_df['avg_rating'].mean(),
            'avg_rating_std': user_features_df['avg_rating'].std(),
            'rating_std_mean': user_features_df['rating_std'].mean(),
            'rating_std_std': user_features_df['rating_std'].std(),
            'rating_count_mean': user_features_df['rating_count'].mean(),
            'rating_count_std': user_features_df['rating_count'].std()
        }
        
        logger.info(f"Extracted features for {len(user_features_df)} users")
        return user_features_df
    
    def extract_movie_features(self, movies_df: pd.DataFrame, ratings_df: pd.DataFrame, movie_id: int) -> np.ndarray:
        """
        Extract movie features including genre embeddings and popularity metrics.
        
        Requirements: 4.2
        """
        movie = movies_df[movies_df['movieId'] == movie_id]
        
        if len(movie) == 0:
            return self._get_default_movie_features()
        
        movie = movie.iloc[0]
        features = []
        
        # Popularity metrics
        movie_ratings = ratings_df[ratings_df['movieId'] == movie_id]
        features.append(len(movie_ratings))  # rating_count
        features.append(movie_ratings['rating'].mean() if len(movie_ratings) > 0 else 0)  # avg_rating
        features.append(movie_ratings['rating'].std() if len(movie_ratings) > 1 else 0)  # rating_std
        
        # Genre embedding (one-hot encoding)
        genre_embedding = self._encode_genres(movie['genres'])
        features.extend(genre_embedding)
        
        return np.array(features)
    
    def extract_movie_features_batch(self, movies_df: pd.DataFrame, ratings_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features for all movies in the dataset.
        
        Requirements: 4.2
        """
        logger.info("Extracting movie features for all movies")
        
        # Build genre list from all movies
        all_genres = set()
        for genres_str in movies_df['genres'].dropna():
            all_genres.update(genres_str.split('|'))
        self.genre_list = sorted(list(all_genres))
        
        movie_features = []
        
        for _, movie in movies_df.iterrows():
            movie_id = movie['movieId']
            movie_ratings = ratings_df[ratings_df['movieId'] == movie_id]
            
            # Popularity metrics
            rating_count = len(movie_ratings)
            avg_rating = movie_ratings['rating'].mean() if len(movie_ratings) > 0 else 0
            rating_std = movie_ratings['rating'].std() if len(movie_ratings) > 1 else 0
            
            # Genre embedding
            genre_embedding = self._encode_genres(movie['genres'])
            
            feature_dict = {
                'movieId': movie_id,
                'rating_count': rating_count,
                'avg_rating': avg_rating,
                'rating_std': rating_std
            }
            
            # Add genre features
            for i, genre in enumerate(self.genre_list):
                feature_dict[f'genre_{genre}'] = genre_embedding[i]
            
            movie_features.append(feature_dict)
        
        movie_features_df = pd.DataFrame(movie_features)
        
        # Store normalization parameters
        self.movie_feature_params = {
            'rating_count_mean': movie_features_df['rating_count'].mean(),
            'rating_count_std': movie_features_df['rating_count'].std(),
            'avg_rating_mean': movie_features_df['avg_rating'].mean(),
            'avg_rating_std': movie_features_df['avg_rating'].std(),
            'rating_std_mean': movie_features_df['rating_std'].mean(),
            'rating_std_std': movie_features_df['rating_std'].std()
        }
        
        logger.info(f"Extracted features for {len(movie_features_df)} movies")
        return movie_features_df
    
    def normalize_user_features(self, user_features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize user features using z-score normalization.
        
        Requirements: 4.3
        """
        logger.info("Normalizing user features")
        
        normalized_df = user_features_df.copy()
        
        # Normalize numerical features
        if 'avg_rating' in normalized_df.columns:
            mean = self.user_feature_params.get('avg_rating_mean', normalized_df['avg_rating'].mean())
            std = self.user_feature_params.get('avg_rating_std', normalized_df['avg_rating'].std())
            if std > 0:
                normalized_df['avg_rating'] = (normalized_df['avg_rating'] - mean) / std
        
        if 'rating_std' in normalized_df.columns:
            mean = self.user_feature_params.get('rating_std_mean', normalized_df['rating_std'].mean())
            std = self.user_feature_params.get('rating_std_std', normalized_df['rating_std'].std())
            if std > 0:
                normalized_df['rating_std'] = (normalized_df['rating_std'] - mean) / std
        
        if 'rating_count' in normalized_df.columns:
            mean = self.user_feature_params.get('rating_count_mean', normalized_df['rating_count'].mean())
            std = self.user_feature_params.get('rating_count_std', normalized_df['rating_count'].std())
            if std > 0:
                normalized_df['rating_count'] = (normalized_df['rating_count'] - mean) / std
        
        return normalized_df
    
    def normalize_movie_features(self, movie_features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize movie features using z-score normalization.
        
        Requirements: 4.3
        """
        logger.info("Normalizing movie features")
        
        normalized_df = movie_features_df.copy()
        
        # Normalize numerical features (genre features are already 0/1)
        if 'rating_count' in normalized_df.columns:
            mean = self.movie_feature_params.get('rating_count_mean', normalized_df['rating_count'].mean())
            std = self.movie_feature_params.get('rating_count_std', normalized_df['rating_count'].std())
            if std > 0:
                normalized_df['rating_count'] = (normalized_df['rating_count'] - mean) / std
        
        if 'avg_rating' in normalized_df.columns:
            mean = self.movie_feature_params.get('avg_rating_mean', normalized_df['avg_rating'].mean())
            std = self.movie_feature_params.get('avg_rating_std', normalized_df['avg_rating'].std())
            if std > 0:
                normalized_df['avg_rating'] = (normalized_df['avg_rating'] - mean) / std
        
        if 'rating_std' in normalized_df.columns:
            mean = self.movie_feature_params.get('rating_std_mean', normalized_df['rating_std'].mean())
            std = self.movie_feature_params.get('rating_std_std', normalized_df['rating_std'].std())
            if std > 0:
                normalized_df['rating_std'] = (normalized_df['rating_std'] - mean) / std
        
        return normalized_df
    
    def _calculate_genre_preferences(self, user_ratings: pd.DataFrame, rated_movies: pd.DataFrame) -> Dict[str, float]:
        """Calculate user's average rating per genre."""
        genre_ratings = {}
        
        for _, movie in rated_movies.iterrows():
            rating = user_ratings[user_ratings['movieId'] == movie['movieId']]['rating'].values
            if len(rating) > 0:
                rating = rating[0]
                genres = movie['genres'].split('|') if pd.notna(movie['genres']) else []
                for genre in genres:
                    if genre not in genre_ratings:
                        genre_ratings[genre] = []
                    genre_ratings[genre].append(rating)
        
        # Calculate average rating per genre
        genre_prefs = {}
        for genre, ratings in genre_ratings.items():
            genre_prefs[f'genre_pref_{genre}'] = np.mean(ratings)
        
        return genre_prefs
    
    def _encode_genres(self, genres_str: str) -> List[float]:
        """One-hot encode movie genres."""
        if pd.isna(genres_str) or not self.genre_list:
            return [0.0] * len(self.genre_list) if self.genre_list else [0.0]
        
        genres = genres_str.split('|')
        encoding = [1.0 if genre in genres else 0.0 for genre in self.genre_list]
        return encoding
    
    def _get_default_user_features(self) -> np.ndarray:
        """Return default features for users with no data."""
        return np.array([3.0, 0.0, 0.0, 0.5, 5.0])  # avg, std, count, min, max
    
    def _get_default_movie_features(self) -> np.ndarray:
        """Return default features for movies with no data."""
        default_features = [0.0, 0.0, 0.0]  # count, avg, std
        default_features.extend([0.0] * len(self.genre_list))  # genre embedding
        return np.array(default_features)
    
    def handle_missing_values(self, features_df: pd.DataFrame, strategy: str = 'mean') -> pd.DataFrame:
        """
        Handle missing values in feature dataframe using specified imputation strategy.
        
        Requirements: 4.4
        
        Args:
            features_df: DataFrame with features that may contain missing values
            strategy: Imputation strategy - 'mean', 'median', 'zero', or 'forward_fill'
        
        Returns:
            DataFrame with missing values imputed
        """
        logger.info(f"Handling missing values using {strategy} strategy")
        
        df = features_df.copy()
        
        # Identify columns with missing values
        missing_cols = df.columns[df.isnull().any()].tolist()
        
        if not missing_cols:
            logger.info("No missing values found")
            return df
        
        logger.info(f"Found missing values in columns: {missing_cols}")
        
        for col in missing_cols:
            missing_count = df[col].isnull().sum()
            logger.info(f"Column '{col}' has {missing_count} missing values")
            
            if strategy == 'mean':
                # Use mean for numerical columns
                if pd.api.types.is_numeric_dtype(df[col]):
                    fill_value = df[col].mean()
                    df[col] = df[col].fillna(fill_value)
                else:
                    # For non-numeric, use mode
                    fill_value = df[col].mode()[0] if len(df[col].mode()) > 0 else 0
                    df[col] = df[col].fillna(fill_value)
            
            elif strategy == 'median':
                # Use median for numerical columns
                if pd.api.types.is_numeric_dtype(df[col]):
                    fill_value = df[col].median()
                    df[col] = df[col].fillna(fill_value)
                else:
                    # For non-numeric, use mode
                    fill_value = df[col].mode()[0] if len(df[col].mode()) > 0 else 0
                    df[col] = df[col].fillna(fill_value)
            
            elif strategy == 'zero':
                # Fill with zero
                df[col] = df[col].fillna(0)
            
            elif strategy == 'forward_fill':
                # Forward fill (use previous value)
                df[col] = df[col].fillna(method='ffill')
                # If still missing (at the beginning), use backward fill
                df[col] = df[col].fillna(method='bfill')
                # If still missing, use zero
                df[col] = df[col].fillna(0)
            
            else:
                raise ValueError(f"Unknown imputation strategy: {strategy}")
        
        logger.info("Missing values handled successfully")
        return df
    
    def validate_features(self, features_df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate that features don't contain invalid values (NaN, inf).
        
        Requirements: 4.4
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check for NaN values
        nan_cols = features_df.columns[features_df.isnull().any()].tolist()
        if nan_cols:
            issues.append(f"NaN values found in columns: {nan_cols}")
        
        # Check for infinite values
        numeric_cols = features_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if np.isinf(features_df[col]).any():
                issues.append(f"Infinite values found in column: {col}")
        
        is_valid = len(issues) == 0
        
        if is_valid:
            logger.info("Feature validation passed")
        else:
            logger.warning(f"Feature validation failed: {issues}")
        
        return is_valid, issues
    
    def save_feature_metadata(self, filepath: str = 'backend/models/feature_metadata.json') -> None:
        """
        Save feature extraction parameters to disk for reproducibility.
        
        Requirements: 4.5
        
        Args:
            filepath: Path to save the metadata JSON file
        """
        logger.info(f"Saving feature metadata to {filepath}")
        
        metadata = {
            'user_feature_params': self.user_feature_params,
            'movie_feature_params': self.movie_feature_params,
            'genre_list': self.genre_list,
            'version': '1.0.0',
            'feature_extraction_config': {
                'user_features': [
                    'avg_rating',
                    'rating_std',
                    'rating_count',
                    'min_rating',
                    'max_rating',
                    'genre_preferences'
                ],
                'movie_features': [
                    'rating_count',
                    'avg_rating',
                    'rating_std',
                    'genre_embedding'
                ]
            }
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("Feature metadata saved successfully")
    
    def load_feature_metadata(self, filepath: str = 'backend/models/feature_metadata.json') -> bool:
        """
        Load feature extraction parameters from disk.
        
        Requirements: 4.5
        
        Args:
            filepath: Path to the metadata JSON file
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not os.path.exists(filepath):
            logger.warning(f"Feature metadata file not found: {filepath}")
            return False
        
        logger.info(f"Loading feature metadata from {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                metadata = json.load(f)
            
            self.user_feature_params = metadata.get('user_feature_params', {})
            self.movie_feature_params = metadata.get('movie_feature_params', {})
            self.genre_list = metadata.get('genre_list', [])
            
            logger.info("Feature metadata loaded successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error loading feature metadata: {e}")
            return False
    
    def get_feature_metadata(self) -> Dict:
        """
        Get current feature extraction parameters.
        
        Requirements: 4.5
        
        Returns:
            Dictionary containing all feature metadata
        """
        return {
            'user_feature_params': self.user_feature_params,
            'movie_feature_params': self.movie_feature_params,
            'genre_list': self.genre_list,
            'n_user_features': 5 + len(self.genre_list),  # base features + genre prefs
            'n_movie_features': 3 + len(self.genre_list)  # base features + genre embedding
        }
