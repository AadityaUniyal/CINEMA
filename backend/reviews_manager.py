"""Movie Reviews and Comments Manager"""
from datetime import datetime
from pymongo import DESCENDING

class ReviewsManager:
    def __init__(self, db):
        self.db = db
        self.reviews_collection = db['reviews'] if db is not None else None
    
    def add_review(self, user_id, movie_id, rating, comment):
        if self.reviews_collection is None:
            return {'error': 'Database not available'}
        
        review = {
            'userId': user_id,
            'movieId': movie_id,
            'rating': rating,
            'comment': comment,
            'timestamp': datetime.now(),
            'likes': 0
        }
        
        self.reviews_collection.update_one(
            {'userId': user_id, 'movieId': movie_id},
            {'$set': review},
            upsert=True
        )
        
        return {'success': True, 'review': review}
    
    def get_movie_reviews(self, movie_id, limit=20):
        if self.reviews_collection is None:
            return []
        
        reviews = list(self.reviews_collection.find(
            {'movieId': movie_id},
            {'_id': 0}
        ).sort('timestamp', DESCENDING).limit(limit))
        
        if reviews and self.db is not None:
            user_ids = [r['userId'] for r in reviews]
            user_profiles = list(self.db['user_profiles'].find(
                {'userId': {'$in': user_ids}},
                {'userId': 1, 'name': 1, '_id': 0}
            ))
            
            user_names = {p['userId']: p['name'] for p in user_profiles}
            
            for review in reviews:
                review['userName'] = user_names.get(review['userId'], f"User {review['userId']}")
        
        return reviews
    
    def get_user_reviews(self, user_id, limit=20):
        if self.reviews_collection is None:
            return []
        
        reviews = list(self.reviews_collection.find(
            {'userId': user_id},
            {'_id': 0}
        ).sort('timestamp', DESCENDING).limit(limit))
        
        return reviews
    
    def like_review(self, user_id, movie_id, reviewer_id):
        if self.reviews_collection is None:
            return {'error': 'Database not available'}
        
        result = self.reviews_collection.update_one(
            {'userId': reviewer_id, 'movieId': movie_id},
            {'$inc': {'likes': 1}}
        )
        
        return {'success': result.modified_count > 0}
    
    def delete_review(self, user_id, movie_id):
        if self.reviews_collection is None:
            return {'error': 'Database not available'}
        
        result = self.reviews_collection.delete_one({
            'userId': user_id,
            'movieId': movie_id
        })
        
        return {'success': result.deleted_count > 0}
