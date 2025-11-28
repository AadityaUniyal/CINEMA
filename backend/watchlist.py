from datetime import datetime

class WatchlistManager:
    def __init__(self, db):
        self.db = db
        self.collection = db['watchlists'] if db else None
    
    def add_to_watchlist(self, user_id, movie_id):
        """Add movie to user's watchlist"""
        if not self.collection:
            return False
        
        watchlist_item = {
            'userId': user_id,
            'movieId': movie_id,
            'addedAt': datetime.now(),
            'watched': False
        }
        
        # Check if already exists
        existing = self.collection.find_one({'userId': user_id, 'movieId': movie_id})
        if existing:
            return False
        
        self.collection.insert_one(watchlist_item)
        return True
    
    def remove_from_watchlist(self, user_id, movie_id):
        """Remove movie from watchlist"""
        if not self.collection:
            return False
        
        result = self.collection.delete_one({'userId': user_id, 'movieId': movie_id})
        return result.deleted_count > 0
    
    def get_watchlist(self, user_id):
        """Get user's watchlist"""
        if not self.collection:
            return []
        
        watchlist = list(self.collection.find({'userId': user_id, 'watched': False}))
        return [{'movieId': item['movieId'], 'addedAt': item['addedAt']} for item in watchlist]
    
    def mark_as_watched(self, user_id, movie_id):
        """Mark movie as watched"""
        if not self.collection:
            return False
        
        result = self.collection.update_one(
            {'userId': user_id, 'movieId': movie_id},
            {'$set': {'watched': True, 'watchedAt': datetime.now()}}
        )
        return result.modified_count > 0
    
    def get_watched_movies(self, user_id):
        """Get user's watched movies"""
        if not self.collection:
            return []
        
        watched = list(self.collection.find({'userId': user_id, 'watched': True}))
        return [{'movieId': item['movieId'], 'watchedAt': item.get('watchedAt')} for item in watched]
