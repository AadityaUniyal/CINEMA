from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
from io import BytesIO
from data_processor import DataProcessor
from ml_engine import RecommendationEngine
from config import Config
from cache_manager import cache, cached
from watchlist import WatchlistManager
from export_service import ExportService
from user_manager import UserManager
from auth import AuthManager
from reviews_manager import ReviewsManager
from user_auth import UserAuth

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.JWT_SECRET_KEY
CORS(app, supports_credentials=True, origins=['*'])

print("Initializing application...")
data_processor = DataProcessor(use_mongodb=False)
ml_engine = RecommendationEngine(data_processor)
try:
    mongo_client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=2000)
    mongo_client.server_info()
    db = mongo_client[Config.DB_NAME]
    user_ratings_collection = db['user_ratings']
    user_history_collection = db['user_history']
    watchlist_manager = WatchlistManager(db)
    user_manager = UserManager(db)
    reviews_manager = ReviewsManager(db)
    user_auth = UserAuth()
    print("✅ MongoDB connected successfully!")
except Exception as e:
    print(f"⚠️  MongoDB not available: {e}")
    print("⚠️  Running in CSV-only mode (auth features disabled)")
    db = None
    watchlist_manager = WatchlistManager(None)
    user_manager = UserManager(None)
    reviews_manager = None
    user_auth = None

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/movies', methods=['GET'])
def get_movies():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', Config.ITEMS_PER_PAGE))
    genre = request.args.get('genre', None)
    
    movies_df = data_processor.get_movie_stats()
    
    if genre:
        movies_df = movies_df[movies_df['genres'].str.contains(genre, case=False, na=False)]
    
    movies_df = movies_df.sort_values(['rating_count', 'avg_rating'], ascending=False)
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    movies_page = movies_df.iloc[start_idx:end_idx]
    
    return jsonify({
        'movies': movies_page.to_dict('records'),
        'page': page,
        'per_page': per_page,
        'total': len(movies_df),
        'total_pages': (len(movies_df) + per_page - 1) // per_page
    })

@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    movie = data_processor.movies[data_processor.movies['movieId'] == movie_id]
    
    if movie.empty:
        return jsonify({'error': 'Movie not found'}), 404
    
    movie_data = movie.iloc[0].to_dict()
    
    ratings = data_processor.ratings[data_processor.ratings['movieId'] == movie_id]
    movie_data['avg_rating'] = float(ratings['rating'].mean()) if len(ratings) > 0 else 0
    movie_data['rating_count'] = len(ratings)
    
    similar_movies = ml_engine.get_content_based_recommendations(movie_id, n=6)
    movie_data['similar_movies'] = similar_movies
    
    return jsonify(movie_data)

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    n = int(request.args.get('n', Config.N_RECOMMENDATIONS))
    
    recommended_ids = ml_engine.get_hybrid_recommendations(user_id, n)
    
    recommended_movies = data_processor.movies[
        data_processor.movies['movieId'].isin(recommended_ids)
    ]
    
    movies_with_stats = data_processor.get_movie_stats()
    result = recommended_movies.merge(
        movies_with_stats[['movieId', 'avg_rating', 'rating_count']],
        on='movieId',
        how='left'
    )
    
    return jsonify({
        'user_id': user_id,
        'recommendations': result.to_dict('records')
    })

@app.route('/api/search', methods=['GET'])
def search_movies():
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', Config.MAX_SEARCH_RESULTS))
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    results = data_processor.search_movies(query, limit)
    return jsonify({'results': results, 'count': len(results)})

@app.route('/api/analytics/top-rated', methods=['GET'])
def get_top_rated():
    min_ratings = int(request.args.get('min_ratings', 50))
    limit = int(request.args.get('limit', 20))
    
    top_movies = data_processor.get_top_rated_movies(min_ratings, limit)
    return jsonify({'top_rated': top_movies})

@app.route('/api/analytics/genre-distribution', methods=['GET'])
def get_genre_distribution():
    distribution = data_processor.get_genre_distribution()
    return jsonify({'distribution': distribution})

@app.route('/api/analytics/rating-distribution', methods=['GET'])
def get_rating_distribution():
    rating_counts = data_processor.ratings['rating'].value_counts().sort_index()
    return jsonify({
        'distribution': rating_counts.to_dict()
    })

@app.route('/api/analytics/trends', methods=['GET'])
def get_trends():
    ratings_df = data_processor.ratings.copy()
    ratings_df['date'] = pd.to_datetime(ratings_df['timestamp'], unit='s')
    ratings_df['year'] = ratings_df['date'].dt.year
    
    yearly_stats = ratings_df.groupby('year').agg({
        'rating': ['mean', 'count']
    }).reset_index()
    yearly_stats.columns = ['year', 'avg_rating', 'count']
    
    return jsonify({
        'yearly_trends': yearly_stats.to_dict('records')
    })

@app.route('/api/rate', methods=['POST'])
def rate_movie():
    data = request.json
    user_id = data.get('userId')
    movie_id = data.get('movieId')
    rating = data.get('rating')
    
    if not all([user_id, movie_id, rating]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if db:
        rating_doc = {
            'userId': user_id,
            'movieId': movie_id,
            'rating': rating,
            'timestamp': datetime.now()
        }
        user_ratings_collection.insert_one(rating_doc)
    
    return jsonify({'success': True, 'message': 'Rating submitted'})

@app.route('/api/user/<int:user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    stats = data_processor.get_user_rating_stats(user_id)
    
    if not stats:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(stats)

@app.route('/api/genres', methods=['GET'])
def get_genres():
    all_genres = set()
    for genres_list in data_processor.movies['genres_list']:
        if isinstance(genres_list, list):
            all_genres.update(genres_list)
    
    return jsonify({'genres': sorted(list(all_genres))})

@app.route('/api/watchlist/<int:user_id>', methods=['GET'])
def get_watchlist(user_id):
    watchlist = watchlist_manager.get_watchlist(user_id)
    
    movie_ids = [item['movieId'] for item in watchlist]
    movies = data_processor.movies[data_processor.movies['movieId'].isin(movie_ids)]
    movies_with_stats = data_processor.get_movie_stats()
    result = movies.merge(
        movies_with_stats[['movieId', 'avg_rating', 'rating_count']],
        on='movieId',
        how='left'
    )
    
    return jsonify({'watchlist': result.to_dict('records')})

@app.route('/api/watchlist/<int:user_id>/<int:movie_id>', methods=['POST'])
def add_to_watchlist(user_id, movie_id):
    success = watchlist_manager.add_to_watchlist(user_id, movie_id)
    if success:
        return jsonify({'success': True, 'message': 'Added to watchlist'})
    return jsonify({'success': False, 'message': 'Already in watchlist'}), 400

@app.route('/api/watchlist/<int:user_id>/<int:movie_id>', methods=['DELETE'])
def remove_from_watchlist(user_id, movie_id):
    success = watchlist_manager.remove_from_watchlist(user_id, movie_id)
    if success:
        return jsonify({'success': True, 'message': 'Removed from watchlist'})
    return jsonify({'success': False, 'message': 'Not found in watchlist'}), 404

@app.route('/api/watchlist/<int:user_id>/<int:movie_id>/watched', methods=['PUT'])
def mark_watched(user_id, movie_id):
    success = watchlist_manager.mark_as_watched(user_id, movie_id)
    if success:
        return jsonify({'success': True, 'message': 'Marked as watched'})
    return jsonify({'success': False, 'message': 'Failed to update'}), 400

@app.route('/api/export/user/<int:user_id>', methods=['GET'])
def export_user_data(user_id):
    format_type = request.args.get('format', 'json')
    user_data = ExportService.export_user_data(user_id, data_processor, db)
    
    if format_type == 'csv':
        csv_data = ExportService.export_to_csv(
            user_data['ratings'],
            ['userId', 'movieId', 'rating', 'timestamp']
        )
        return csv_data, 200, {'Content-Type': 'text/csv', 'Content-Disposition': f'attachment; filename=user_{user_id}_data.csv'}
    
    return jsonify(user_data)

@app.route('/api/export/recommendations/<int:user_id>', methods=['GET'])
def export_recommendations(user_id):
    n = int(request.args.get('n', Config.N_RECOMMENDATIONS))
    recommended_ids = ml_engine.get_hybrid_recommendations(user_id, n)
    report = ExportService.export_recommendations_report(user_id, recommended_ids, data_processor)
    
    return jsonify(report)

@app.route('/api/similar-users/<int:user_id>', methods=['GET'])
def get_similar_users(user_id):
    n = int(request.args.get('n', 5))
    similar_users = ml_engine.get_similar_users(user_id, n)
    
    users_stats = []
    for uid in similar_users:
        stats = data_processor.get_user_rating_stats(uid)
        if stats:
            stats['userId'] = uid
            users_stats.append(stats)
    
    return jsonify({'similar_users': users_stats})

@app.route('/api/movies/random', methods=['GET'])
def get_random_movies():
    n = int(request.args.get('n', 10))
    genre = request.args.get('genre', None)
    
    movies_df = data_processor.get_movie_stats()
    
    if genre:
        movies_df = movies_df[movies_df['genres'].str.contains(genre, case=False, na=False)]
    
    movies_df = movies_df[movies_df['rating_count'] >= 10]
    
    random_movies = movies_df.sample(n=min(n, len(movies_df)))
    return jsonify({'movies': random_movies.to_dict('records')})

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    cache.clear()
    return jsonify({'success': True, 'message': 'Cache cleared'})

@app.route('/api/analytics/user-activity', methods=['GET'])
def get_user_activity():
    total_users = data_processor.ratings['userId'].nunique()
    total_ratings = len(data_processor.ratings)
    avg_ratings_per_user = total_ratings / total_users if total_users > 0 else 0
    
    user_activity = data_processor.ratings.groupby('userId').size().reset_index(name='rating_count')
    top_users = user_activity.nlargest(10, 'rating_count')
    
    return jsonify({
        'total_users': int(total_users),
        'total_ratings': int(total_ratings),
        'avg_ratings_per_user': float(avg_ratings_per_user),
        'most_active_users': top_users.to_dict('records')
    })

    
    return jsonify({
        'success': True,
        'token': token,
        'user': user
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/preferences/setup', methods=['POST'])
def setup_preferences():
    data = request.json
    user_id = data.get('user_id')
    preferred_genres = data.get('preferred_genres', [])
    favorite_tags = data.get('favorite_tags', [])
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    success = user_manager.save_preferences(user_id, preferred_genres, favorite_tags)
    if success:
        return jsonify({'success': True, 'message': 'Preferences saved'})
    return jsonify({'error': 'Failed to save preferences'}), 500

@app.route('/api/preferences/<user_id>', methods=['GET'])
def get_user_preferences(user_id):
    preferences = user_manager.get_preferences(user_id)
    if preferences:
        return jsonify({
            'preferred_genres': preferences.get('preferred_genres', []),
            'favorite_tags': preferences.get('favorite_tags', [])
        })
    return jsonify({'preferred_genres': [], 'favorite_tags': []})

@app.route('/api/tags', methods=['GET'])
def get_all_tags():
    if data_processor.tags is not None and not data_processor.tags.empty:
        all_tags = data_processor.tags['tag'].unique().tolist()
        tag_counts = data_processor.tags['tag'].value_counts().head(50)
        popular_tags = tag_counts.index.tolist()
        return jsonify({'tags': popular_tags})
    return jsonify({'tags': []})

@app.route('/api/favorites/<user_id>', methods=['GET'])
def get_favorites(user_id):
    favorites = user_manager.get_favorites(user_id)
    
    movie_ids = [fav['movie_id'] for fav in favorites]
    if movie_ids:
        fav_movies = data_processor.movies[data_processor.movies['movieId'].isin(movie_ids)]
        movies_with_stats = data_processor.get_movie_stats()
        result = fav_movies.merge(
            movies_with_stats[['movieId', 'avg_rating', 'rating_count']],
            on='movieId',
            how='left'
        )
        return jsonify({'favorites': result.to_dict('records')})
    
    return jsonify({'favorites': []})

@app.route('/api/favorites/<user_id>/<int:movie_id>', methods=['POST'])
def add_to_favorites(user_id, movie_id):
    success = user_manager.add_favorite(user_id, movie_id)
    if success:
        return jsonify({'success': True, 'message': 'Added to favorites'})
    return jsonify({'success': False, 'message': 'Already in favorites'}), 400

@app.route('/api/favorites/<user_id>/<int:movie_id>', methods=['DELETE'])
def remove_from_favorites(user_id, movie_id):
    success = user_manager.remove_favorite(user_id, movie_id)
    if success:
        return jsonify({'success': True, 'message': 'Removed from favorites'})
    return jsonify({'success': False, 'message': 'Not in favorites'}), 404

@app.route('/api/favorites/<user_id>/<int:movie_id>/check', methods=['GET'])
def check_favorite(user_id, movie_id):
    is_fav = user_manager.is_favorite(user_id, movie_id)
    return jsonify({'is_favorite': is_fav})

@app.route('/api/recommendations/personalized/<user_id>', methods=['GET'])
def get_personalized_recommendations(user_id):
    n = int(request.args.get('n', 20))
    
    preferences = user_manager.get_preferences(user_id)
    
    if preferences and preferences.get('preferred_genres'):
        preferred_genres = preferences['preferred_genres']
        movies_df = data_processor.get_movie_stats()
        
        filtered_movies = movies_df[
            movies_df['genres'].apply(
                lambda x: any(genre in x for genre in preferred_genres)
            )
        ]
        
        filtered_movies = filtered_movies.sort_values(
            ['avg_rating', 'rating_count'], 
            ascending=False
        )
        
        result = filtered_movies.head(n)
        return jsonify({
            'user_id': user_id,
            'recommendations': result.to_dict('records'),
            'based_on': 'preferences'
        })
    
    return get_recommendations(user_id)

@app.route('/api/reviews/<int:movie_id>', methods=['GET'])
def get_movie_reviews(movie_id):
    if not reviews_manager:
        return jsonify({'reviews': []})
    
    reviews = reviews_manager.get_movie_reviews(movie_id)
    return jsonify({'reviews': reviews})

@app.route('/api/reviews', methods=['POST'])
def add_review():
    if not reviews_manager:
        return jsonify({'error': 'Reviews not available'}), 503
    
    data = request.json
    user_id = data.get('userId')
    movie_id = data.get('movieId')
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    if not all([user_id, movie_id, rating]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    result = reviews_manager.add_review(user_id, movie_id, rating, comment)
    return jsonify(result)

@app.route('/api/reviews/user/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    if not reviews_manager:
        return jsonify({'reviews': []})
    
    reviews = reviews_manager.get_user_reviews(user_id)
    return jsonify({'reviews': reviews})

@app.route('/api/reviews/<int:movie_id>', methods=['DELETE'])
def delete_review(movie_id):
    if not reviews_manager:
        return jsonify({'error': 'Reviews not available'}), 503
    
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    result = reviews_manager.delete_review(int(user_id), movie_id)
    return jsonify(result)

@app.route('/api/analytics/trending-genres', methods=['GET'])
def get_trending_genres():
    limit = int(request.args.get('limit', 10))
    
    genre_dist = data_processor.get_genre_distribution()
    
    sorted_genres = sorted(genre_dist.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    trending = [{'genre': genre, 'count': count} for genre, count in sorted_genres]
    return jsonify({'trending_genres': trending})

@app.route('/api/auth/register', methods=['POST'])
def register():
    if not user_auth:
        return jsonify({'error': 'Authentication service not available'}), 503
    
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not all([name, email, password]):
        return jsonify({'error': 'Name, email, and password are required'}), 400
    
    success, message, user_id = user_auth.register_user(name, email, password)
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'userId': user_id
        }), 201
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    if not user_auth:
        return jsonify({'error': 'Authentication service not available'}), 503
    
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({'error': 'Email and password are required'}), 400
    
    success, message, user_id, user_data = user_auth.login_user(email, password)
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'userId': user_id,
            'user': user_data
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 401

@app.route('/api/auth/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    if not user_auth:
        return jsonify({'error': 'Authentication service not available'}), 503
    
    profile = user_auth.get_user_profile(user_id)
    
    if profile:
        return jsonify({
            'success': True,
            'profile': profile
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': 'Profile not found'
        }), 404

@app.route('/api/user/preferences', methods=['POST'])
def save_user_preferences():
    if not user_auth:
        return jsonify({'error': 'Authentication service not available'}), 503
    
    data = request.json
    user_id = data.get('userId')
    preferred_genres = data.get('preferredGenres', [])
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    try:
        if user_auth.user_profiles_collection:
            user_auth.user_profiles_collection.update_one(
                {'userId': user_id},
                {'$set': {'preferredGenres': preferred_genres}},
                upsert=True
            )
            return jsonify({
                'success': True,
                'message': 'Preferences saved successfully'
            }), 200
        else:
            return jsonify({'error': 'Database not available'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask server...")
    print(f"Loaded {len(data_processor.movies)} movies")
    print(f"Loaded {len(data_processor.ratings)} ratings")
    app.run(debug=True, port=5000)
