"""
Test script for hyperparameter tuning API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_get_default_hyperparameters():
    """Test getting default hyperparameters"""
    print("Test: Get Default Hyperparameters")
    print("-" * 50)
    
    response = requests.get(f"{BASE_URL}/api/ml/hyperparameters/default/matrix_factorization")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"  Model Type: {data['model_type']}")
        print(f"  Hyperparameters: {json.dumps(data['hyperparameters'], indent=2)}")
    else:
        print(f"✗ Status: {response.status_code}")
        print(f"  Error: {response.text}")
    print()

def test_get_parameter_ranges():
    """Test getting parameter ranges"""
    print("Test: Get Parameter Ranges")
    print("-" * 50)
    
    response = requests.get(f"{BASE_URL}/api/ml/hyperparameters/ranges/matrix_factorization")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"  Model Type: {data['model_type']}")
        print(f"  Ranges: {json.dumps(data['ranges'], indent=2)}")
    else:
        print(f"✗ Status: {response.status_code}")
        print(f"  Error: {response.text}")
    print()

def test_validate_hyperparameters():
    """Test hyperparameter validation"""
    print("Test: Validate Hyperparameters")
    print("-" * 50)
    
    # Valid config
    valid_payload = {
        "model_type": "matrix_factorization",
        "hyperparameters": {
            "n_factors": 50,
            "learning_rate": 0.01,
            "regularization": 0.02,
            "epochs": 20
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ml/hyperparameters/validate",
        json=valid_payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Valid config - Status: {response.status_code}")
        print(f"  Valid: {data['valid']}")
        print(f"  Errors: {data['errors']}")
    else:
        print(f"✗ Status: {response.status_code}")
        print(f"  Error: {response.text}")
    
    # Invalid config
    invalid_payload = {
        "model_type": "matrix_factorization",
        "hyperparameters": {
            "n_factors": 500,
            "learning_rate": 2.0
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ml/hyperparameters/validate",
        json=invalid_payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Invalid config - Status: {response.status_code}")
        print(f"  Valid: {data['valid']}")
        print(f"  Errors: {data['errors']}")
    else:
        print(f"✗ Status: {response.status_code}")
        print(f"  Error: {response.text}")
    print()

def test_get_best_hyperparameters():
    """Test getting best hyperparameters"""
    print("Test: Get Best Hyperparameters")
    print("-" * 50)
    
    response = requests.get(f"{BASE_URL}/api/ml/hyperparameters/best/matrix_factorization")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"  Model Type: {data['model_type']}")
        print(f"  Hyperparameters: {json.dumps(data['hyperparameters'], indent=2)}")
    else:
        print(f"✗ Status: {response.status_code}")
        print(f"  Error: {response.text}")
    print()

if __name__ == '__main__':
    print("=" * 50)
    print("Hyperparameter Tuning API Test Suite")
    print("=" * 50)
    print("Note: Flask server must be running on localhost:5000")
    print("=" * 50)
    print()
    
    try:
        test_get_default_hyperparameters()
        test_get_parameter_ranges()
        test_validate_hyperparameters()
        test_get_best_hyperparameters()
        
        print("=" * 50)
        print("API tests completed!")
        print("=" * 50)
    except requests.exceptions.ConnectionError:
        print("=" * 50)
        print("Error: Could not connect to Flask server")
        print("Please start the server with: python app.py")
        print("=" * 50)
    except Exception as e:
        print("=" * 50)
        print(f"Error: {e}")
        print("=" * 50)
