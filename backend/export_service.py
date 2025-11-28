import csv
import json
from io import StringIO
from datetime import datetime

class ExportService:
    @staticmethod
    def export_to_csv(data, columns):
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
    
    @staticmethod
    def export_to_json(data):
        return json.dumps(data, indent=2, default=str)
    
    @staticmethod
    def export_user_data(user_id, data_processor, db):
        user_data = {
            'userId': user_id,
            'exportDate': datetime.now().isoformat(),
            'ratings': [],
            'watchlist': [],
            'statistics': {}
        }
        
        user_ratings = data_processor.ratings[data_processor.ratings['userId'] == user_id]
        user_data['ratings'] = user_ratings.to_dict('records')
        
        if db:
            watchlist = list(db['watchlists'].find({'userId': user_id}))
            user_data['watchlist'] = [{'movieId': item['movieId'], 'addedAt': str(item['addedAt'])} for item in watchlist]
        
        stats = data_processor.get_user_rating_stats(user_id)
        if stats:
            user_data['statistics'] = stats
        
        return user_data
    
    @staticmethod
    def export_recommendations_report(user_id, recommendations, data_processor):
        report = {
            'userId': user_id,
            'generatedAt': datetime.now().isoformat(),
            'recommendations': []
        }
        
        for movie_id in recommendations:
            movie = data_processor.movies[data_processor.movies['movieId'] == movie_id]
            if not movie.empty:
                movie_data = movie.iloc[0].to_dict()
                ratings = data_processor.ratings[data_processor.ratings['movieId'] == movie_id]
                movie_data['avg_rating'] = float(ratings['rating'].mean()) if len(ratings) > 0 else 0
                movie_data['rating_count'] = len(ratings)
                report['recommendations'].append(movie_data)
        
        return report
