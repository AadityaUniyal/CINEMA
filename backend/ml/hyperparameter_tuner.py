import json
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.model_selection import KFold
from ml.matrix_factorization import MatrixFactorizationModel
from ml.evaluation_service import EvaluationService
from ml.ml_logger import get_ml_logger

logger = get_ml_logger('hyperparameter_tuner')

class HyperparameterTuner:
    def __init__(self, config_path='ml/hyperparameter_config.json'):
        self.config_path = config_path
        self.config = self._load_config()
        self.best_configs = {}
        self.tuning_history = []
        
    def _load_config(self) -> Dict:
        """Load hyperparameter configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded hyperparameter config from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
    
    def get_default_hyperparams(self, model_type: str) -> Dict:
        """Get default hyperparameters for a model type"""
        if model_type not in self.config:
            raise ValueError(f"Unknown model type: {model_type}")
        return self.config[model_type]['default'].copy()
    
    def get_param_ranges(self, model_type: str) -> Dict:
        """Get valid parameter ranges for a model type"""
        if model_type not in self.config:
            raise ValueError(f"Unknown model type: {model_type}")
        return self.config[model_type]['ranges'].copy()
    
    def validate_hyperparams(self, model_type: str, hyperparams: Dict) -> Tuple[bool, List[str]]:
        """
        Validate hyperparameters against configured ranges
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if model_type not in self.config:
            return False, [f"Unknown model type: {model_type}"]
        
        ranges = self.config[model_type]['ranges']
        errors = []
        
        for param_name, param_value in hyperparams.items():
            if param_name not in ranges:
                continue
            
            param_range = ranges[param_name]
            param_type = param_range['type']
            min_val = param_range['min']
            max_val = param_range['max']
            
            # Type validation
            if param_type == 'int' and not isinstance(param_value, int):
                errors.append(f"{param_name} must be an integer")
                continue
            elif param_type == 'float' and not isinstance(param_value, (int, float)):
                errors.append(f"{param_name} must be a number")
                continue
            
            # Range validation
            if param_value < min_val or param_value > max_val:
                errors.append(f"{param_name} must be between {min_val} and {max_val}")
        
        return len(errors) == 0, errors

    
    def cross_validate(self, model_type: str, ratings_df, hyperparams: Dict, 
                      n_splits: int = 5) -> Dict:
        """
        Perform K-fold cross-validation for a given hyperparameter configuration
        
        Args:
            model_type: Type of model to train
            ratings_df: DataFrame with ratings data
            hyperparams: Hyperparameter configuration to test
            n_splits: Number of folds for cross-validation
            
        Returns:
            Dictionary with mean and std of metrics across folds
        """
        logger.info(f"Starting {n_splits}-fold cross-validation for {model_type}")
        logger.info(f"Hyperparameters: {hyperparams}")
        
        # Validate hyperparameters
        is_valid, errors = self.validate_hyperparams(model_type, hyperparams)
        if not is_valid:
            raise ValueError(f"Invalid hyperparameters: {', '.join(errors)}")
        
        kfold = KFold(n_splits=n_splits, shuffle=True, random_state=42)
        
        fold_metrics = {
            'rmse': [],
            'precision_at_10': [],
            'recall_at_10': [],
            'coverage': []
        }
        
        eval_service = EvaluationService()
        
        for fold_idx, (train_idx, test_idx) in enumerate(kfold.split(ratings_df)):
            logger.info(f"Training fold {fold_idx + 1}/{n_splits}")
            
            train_df = ratings_df.iloc[train_idx]
            test_df = ratings_df.iloc[test_idx]
            
            # Train model
            if model_type == 'matrix_factorization':
                model = MatrixFactorizationModel(**hyperparams)
                model.fit(train_df, verbose=False)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Evaluate model
            metrics = eval_service.evaluate_model(model, test_df)
            
            for metric_name, metric_value in metrics.items():
                if metric_name in fold_metrics:
                    fold_metrics[metric_name].append(metric_value)
        
        # Calculate mean and std across folds
        results = {}
        for metric_name, values in fold_metrics.items():
            results[f'{metric_name}_mean'] = np.mean(values)
            results[f'{metric_name}_std'] = np.std(values)
        
        logger.info(f"Cross-validation complete. RMSE: {results['rmse_mean']:.4f} ± {results['rmse_std']:.4f}")
        
        return results
    
    def grid_search(self, model_type: str, ratings_df, n_splits: int = 5) -> Dict:
        """
        Perform grid search over predefined hyperparameter configurations
        
        Args:
            model_type: Type of model to tune
            ratings_df: DataFrame with ratings data
            n_splits: Number of folds for cross-validation
            
        Returns:
            Dictionary with best configuration and all results
        """
        logger.info(f"Starting grid search for {model_type}")
        
        if model_type not in self.config:
            raise ValueError(f"Unknown model type: {model_type}")
        
        if 'search_space' not in self.config[model_type]:
            logger.warning(f"No search space defined for {model_type}, using default params")
            return {
                'best_config': self.get_default_hyperparams(model_type),
                'best_score': None,
                'all_results': []
            }
        
        search_space = self.config[model_type]['search_space']
        all_results = []
        best_score = float('inf')
        best_config = None
        
        for idx, hyperparams in enumerate(search_space):
            logger.info(f"Testing configuration {idx + 1}/{len(search_space)}")
            
            try:
                cv_results = self.cross_validate(model_type, ratings_df, hyperparams, n_splits)
                
                result = {
                    'hyperparams': hyperparams,
                    'metrics': cv_results,
                    'score': cv_results['rmse_mean']  # Lower is better
                }
                all_results.append(result)
                
                # Track best configuration (lowest RMSE)
                if cv_results['rmse_mean'] < best_score:
                    best_score = cv_results['rmse_mean']
                    best_config = hyperparams.copy()
                    logger.info(f"New best configuration found! RMSE: {best_score:.4f}")
                
            except Exception as e:
                logger.error(f"Error testing configuration {idx + 1}: {e}")
                continue
        
        if best_config is None:
            logger.warning("No valid configuration found, using default")
            best_config = self.get_default_hyperparams(model_type)
        
        # Store best configuration
        self.best_configs[model_type] = best_config
        
        # Add to tuning history
        self.tuning_history.append({
            'model_type': model_type,
            'best_config': best_config,
            'best_score': best_score,
            'timestamp': pd.Timestamp.now().isoformat()
        })
        
        logger.info(f"Grid search complete. Best RMSE: {best_score:.4f}")
        logger.info(f"Best configuration: {best_config}")
        
        return {
            'best_config': best_config,
            'best_score': best_score,
            'all_results': all_results
        }
    
    def get_best_config(self, model_type: str) -> Dict:
        """Get the best known configuration for a model type"""
        if model_type in self.best_configs:
            return self.best_configs[model_type].copy()
        return self.get_default_hyperparams(model_type)
    
    def save_best_configs(self, filepath: str = 'backend/models/best_hyperparams.json'):
        """Save best configurations to file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump({
                    'best_configs': self.best_configs,
                    'tuning_history': self.tuning_history
                }, f, indent=2)
            logger.info(f"Saved best configurations to {filepath}")
        except Exception as e:
            logger.error(f"Error saving best configs: {e}")
            raise
    
    def load_best_configs(self, filepath: str = 'backend/models/best_hyperparams.json'):
        """Load best configurations from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.best_configs = data.get('best_configs', {})
                self.tuning_history = data.get('tuning_history', [])
            logger.info(f"Loaded best configurations from {filepath}")
        except FileNotFoundError:
            logger.info(f"No saved configurations found at {filepath}")
        except Exception as e:
            logger.error(f"Error loading best configs: {e}")
            raise
