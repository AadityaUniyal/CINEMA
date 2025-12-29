import numpy as np
from sklearn.metrics import mean_squared_error
from ml.ml_logger import get_ml_logger
logger = get_ml_logger('evaluation_service')
class EvaluationService:
    
    def evaluate_model(self, model, test_df):
        logger.info(f"Evaluating model on {len(test_df)} test samples")
        
        predictions = []
        actuals = []
        
        for _, row in test_df.iterrows():
            pred = model.predict(row['userId'], row['movieId'])
            predictions.append(pred)
            actuals.append(row['rating'])
        
        rmse = self.calculate_rmse(predictions, actuals)
        
        user_recommendations = {}
        for user_id in test_df['userId'].unique()[:100]:
            rated_movies = test_df[test_df['userId'] == user_id]['movieId'].tolist()
            recs = model.recommend(user_id, n=10, exclude_rated=True, rated_movies=rated_movies)
            user_recommendations[user_id] = recs
        
        precision_10 = self.calculate_precision_at_k(user_recommendations, test_df, k=10)
        recall_10 = self.calculate_recall_at_k(user_recommendations, test_df, k=10)
        
        all_movies = test_df['movieId'].unique()
        coverage = self.calculate_coverage(user_recommendations, all_movies)
        
        metrics = {
            'rmse': float(rmse),
            'precision_at_10': float(precision_10),
            'recall_at_10': float(recall_10),
            'coverage': float(coverage)
        }
        
        logger.info(f"Evaluation complete: RMSE={rmse:.4f}, P@10={precision_10:.4f}, R@10={recall_10:.4f}, Coverage={coverage:.4f}")
        return metrics
    
    def calculate_rmse(self, predictions, actuals):
        return np.sqrt(mean_squared_error(actuals, predictions))
    
    def calculate_precision_at_k(self, recommendations, test_df, k=10):
        precisions = []
        
        for user_id, recs in recommendations.items():
            relevant = test_df[(test_df['userId'] == user_id) & (test_df['rating'] >= 4.0)]['movieId'].tolist()
            
            if not relevant:
                continue
            
            recs_k = recs[:k]
            relevant_in_recs = len(set(recs_k) & set(relevant))
            precision = relevant_in_recs / k if k > 0 else 0
            precisions.append(precision)
        
        return np.mean(precisions) if precisions else 0.0
    
    def calculate_recall_at_k(self, recommendations, test_df, k=10):
        recalls = []
        
        for user_id, recs in recommendations.items():
            relevant = test_df[(test_df['userId'] == user_id) & (test_df['rating'] >= 4.0)]['movieId'].tolist()
            
            if not relevant:
                continue
            
            recs_k = recs[:k]
            relevant_in_recs = len(set(recs_k) & set(relevant))
            recall = relevant_in_recs / len(relevant) if len(relevant) > 0 else 0
            recalls.append(recall)
        
        return np.mean(recalls) if recalls else 0.0
    
    def calculate_coverage(self, recommendations, all_items):
        recommended_items = set()
        for recs in recommendations.values():
            recommended_items.update(recs)
        
        coverage = len(recommended_items) / len(all_items) if len(all_items) > 0 else 0
        return coverage
    
    def generate_report(self, model, test_df):
        metrics = self.evaluate_model(model, test_df)
        
        report = {
            'metrics': metrics,
            'test_data_size': len(test_df),
            'n_users': len(test_df['userId'].unique()),
            'n_movies': len(test_df['movieId'].unique())
        }
        
        return report
