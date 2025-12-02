"""
Manual test script for hyperparameter tuning functionality
"""
import pandas as pd
import numpy as np
from ml.hyperparameter_tuner import HyperparameterTuner

def create_sample_data(n_users=50, n_movies=100, n_ratings=500):
    """Create sample rating data for testing"""
    np.random.seed(42)
    
    user_ids = np.random.randint(1, n_users + 1, n_ratings)
    movie_ids = np.random.randint(1, n_movies + 1, n_ratings)
    ratings = np.random.uniform(0.5, 5.0, n_ratings)
    
    df = pd.DataFrame({
        'userId': user_ids,
        'movieId': movie_ids,
        'rating': ratings
    })
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['userId', 'movieId'])
    
    return df

def test_config_loading():
    """Test 1: Config loading and default parameters"""
    print("Test 1: Config Loading")
    print("-" * 50)
    
    tuner = HyperparameterTuner()
    default_params = tuner.get_default_hyperparams('matrix_factorization')
    
    print(f"Default parameters: {default_params}")
    assert 'n_factors' in default_params
    assert 'learning_rate' in default_params
    print("✓ Config loaded successfully\n")

def test_validation():
    """Test 2: Hyperparameter validation"""
    print("Test 2: Hyperparameter Validation")
    print("-" * 50)
    
    tuner = HyperparameterTuner()
    
    # Valid config
    valid_config = {'n_factors': 50, 'learning_rate': 0.01, 'regularization': 0.02, 'epochs': 20}
    is_valid, errors = tuner.validate_hyperparams('matrix_factorization', valid_config)
    print(f"Valid config: {is_valid}, Errors: {errors}")
    assert is_valid == True
    
    # Invalid config - n_factors out of range
    invalid_config = {'n_factors': 500}
    is_valid, errors = tuner.validate_hyperparams('matrix_factorization', invalid_config)
    print(f"Invalid config (n_factors=500): {is_valid}, Errors: {errors}")
    assert is_valid == False
    assert len(errors) > 0
    
    # Invalid config - learning_rate out of range
    invalid_config2 = {'learning_rate': 2.0}
    is_valid, errors = tuner.validate_hyperparams('matrix_factorization', invalid_config2)
    print(f"Invalid config (learning_rate=2.0): {is_valid}, Errors: {errors}")
    assert is_valid == False
    
    print("✓ Validation working correctly\n")

def test_cross_validation():
    """Test 3: Cross-validation with sample data"""
    print("Test 3: Cross-Validation")
    print("-" * 50)
    
    tuner = HyperparameterTuner()
    sample_data = create_sample_data(n_users=30, n_movies=50, n_ratings=300)
    
    print(f"Sample data: {len(sample_data)} ratings")
    
    hyperparams = {'n_factors': 10, 'learning_rate': 0.01, 'regularization': 0.02, 'epochs': 5}
    
    try:
        results = tuner.cross_validate('matrix_factorization', sample_data, hyperparams, n_splits=3)
        
        print(f"Cross-validation results:")
        print(f"  RMSE: {results['rmse_mean']:.4f} ± {results['rmse_std']:.4f}")
        print(f"  Precision@10: {results['precision_at_10_mean']:.4f} ± {results['precision_at_10_std']:.4f}")
        
        assert 'rmse_mean' in results
        assert 'rmse_std' in results
        assert results['rmse_mean'] > 0
        
        print("✓ Cross-validation completed successfully\n")
    except Exception as e:
        print(f"✗ Cross-validation failed: {e}\n")
        raise

def test_best_config_tracking():
    """Test 4: Best configuration tracking"""
    print("Test 4: Best Configuration Tracking")
    print("-" * 50)
    
    tuner = HyperparameterTuner()
    
    # Set a best config
    tuner.best_configs['matrix_factorization'] = {
        'n_factors': 70,
        'learning_rate': 0.015,
        'regularization': 0.03,
        'epochs': 25
    }
    
    # Retrieve it
    best_config = tuner.get_best_config('matrix_factorization')
    print(f"Best config: {best_config}")
    assert best_config['n_factors'] == 70
    
    # Save and load
    try:
        tuner.save_best_configs('backend/models/test_best_hyperparams.json')
        print("✓ Saved best configs")
        
        tuner2 = HyperparameterTuner()
        tuner2.load_best_configs('backend/models/test_best_hyperparams.json')
        loaded_config = tuner2.get_best_config('matrix_factorization')
        print(f"Loaded config: {loaded_config}")
        assert loaded_config['n_factors'] == 70
        
        print("✓ Best configuration tracking working\n")
    except Exception as e:
        print(f"✗ Config tracking failed: {e}\n")
        raise

if __name__ == '__main__':
    print("=" * 50)
    print("Hyperparameter Tuning Test Suite")
    print("=" * 50)
    print()
    
    try:
        test_config_loading()
        test_validation()
        test_cross_validation()
        test_best_config_tracking()
        
        print("=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
    except Exception as e:
        print("=" * 50)
        print(f"Tests failed: {e}")
        print("=" * 50)
        raise
