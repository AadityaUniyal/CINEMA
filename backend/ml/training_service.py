import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from ml.matrix_factorization import MatrixFactorizationModel
from ml.ml_model_manager import MLModelManager
from ml.ml_logger import get_ml_logger

logger = get_ml_logger('training_service')

class TrainingService:
    def __init__(self):
        self.model_manager = MLModelManager()
        
    def prepare_data(self, ratings_df, test_size=0.2, random_state=42):
        logger.info(f"Preparing data: {len(ratings_df)} total ratings")
        
        train_df, test_df = train_test_split(
            ratings_df,
            test_size=test_size,
            random_state=random_state
        )
        
        logger.info(f"Train: {len(train_df)}, Test: {len(test_df)}")
        return train_df, test_df
    
    def train_model(self, model_type, ratings_df, hyperparams=None):
        logger.info(f"Training {model_type} model")
        
        train_df, test_df = self.prepare_data(ratings_df)
        
        if model_type == 'matrix_factorization':
            model = self._train_matrix_factorization(train_df, hyperparams)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        return model, train_df, test_df
    
    def _train_matrix_factorization(self, train_df, hyperparams=None):
        if hyperparams is None:
            hyperparams = {
                'n_factors': 50,
                'learning_rate': 0.01,
                'regularization': 0.02,
                'epochs': 20
            }
        
        self._validate_hyperparams(hyperparams)
        
        model = MatrixFactorizationModel(**hyperparams)
        training_history = model.fit(train_df)
        
        return model
    
    def _validate_hyperparams(self, hyperparams):
        if 'n_factors' in hyperparams:
            if not (1 <= hyperparams['n_factors'] <= 200):
                raise ValueError("n_factors must be between 1 and 200")
        
        if 'learning_rate' in hyperparams:
            if not (0.0001 <= hyperparams['learning_rate'] <= 1.0):
                raise ValueError("learning_rate must be between 0.0001 and 1.0")
        
        if 'regularization' in hyperparams:
            if not (0.0 <= hyperparams['regularization'] <= 1.0):
                raise ValueError("regularization must be between 0.0 and 1.0")
        
        if 'epochs' in hyperparams:
            if not (1 <= hyperparams['epochs'] <= 100):
                raise ValueError("epochs must be between 1 and 100")
    
    def retrain_all_models(self, ratings_df):
        logger.info("Retraining all models")
        
        results = {}
        
        try:
            model, train_df, test_df = self.train_model('matrix_factorization', ratings_df)
            
            from ml.evaluation_service import EvaluationService
            eval_service = EvaluationService()
            metrics = eval_service.evaluate_model(model, test_df)
            
            metadata = {
                'hyperparameters': {
                    'n_factors': model.n_factors,
                    'learning_rate': model.learning_rate,
                    'regularization': model.regularization,
                    'epochs': model.epochs
                },
                'metrics': metrics,
                'training_data': {
                    'n_users': len(train_df['userId'].unique()),
                    'n_movies': len(train_df['movieId'].unique()),
                    'n_ratings': len(train_df)
                }
            }
            
            version = self.model_manager.save_model(model, 'matrix_factorization', metadata)
            results['matrix_factorization'] = {
                'version': version,
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Error training matrix_factorization: {e}")
            results['matrix_factorization'] = {'error': str(e)}
        
        return results
