import os
import json
import joblib
from datetime import datetime
from ml.ml_logger import get_ml_logger

logger = get_ml_logger('model_manager')

class MLModelManager:
    def __init__(self, models_dir='backend/models'):
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        
    def save_model(self, model, model_type, metadata=None):
        version = datetime.now().strftime("v%Y%m%d_%H%M%S")
        model_dir = os.path.join(self.models_dir, model_type)
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, f'{version}.pkl')
        joblib.dump(model, model_path)
        
        if metadata is None:
            metadata = {}
        
        metadata['version'] = version
        metadata['model_type'] = model_type
        metadata['saved_at'] = datetime.now().isoformat()
        
        metadata_path = os.path.join(model_dir, f'{version}_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self._update_latest_link(model_dir, version)
        
        logger.info(f"Model saved: {model_type} {version}")
        return version
    
    def load_model(self, model_type, version='latest'):
        model_dir = os.path.join(self.models_dir, model_type)
        
        if not os.path.exists(model_dir):
            logger.warning(f"Model directory not found: {model_dir}")
            return None
        
        if version == 'latest':
            latest_link = os.path.join(model_dir, 'latest.txt')
            if os.path.exists(latest_link):
                with open(latest_link, 'r') as f:
                    version = f.read().strip()
            else:
                versions = self.list_versions(model_type)
                if not versions:
                    return None
                version = versions[-1]['version']
        
        model_path = os.path.join(model_dir, f'{version}.pkl')
        
        if not os.path.exists(model_path):
            logger.warning(f"Model file not found: {model_path}")
            return None
        
        try:
            model = joblib.load(model_path)
            logger.info(f"Model loaded: {model_type} {version}")
            return model
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None
    
    def list_versions(self, model_type):
        model_dir = os.path.join(self.models_dir, model_type)
        
        if not os.path.exists(model_dir):
            return []
        
        versions = []
        for filename in os.listdir(model_dir):
            if filename.endswith('_metadata.json'):
                metadata_path = os.path.join(model_dir, filename)
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    versions.append(metadata)
        
        versions.sort(key=lambda x: x.get('saved_at', ''))
        return versions
    
    def get_best_model(self, model_type, metric='rmse'):
        versions = self.list_versions(model_type)
        
        if not versions:
            return None
        
        valid_versions = [v for v in versions if 'metrics' in v and metric in v['metrics']]
        
        if not valid_versions:
            return self.load_model(model_type, 'latest')
        
        if metric == 'rmse':
            best_version = min(valid_versions, key=lambda x: x['metrics'][metric])
        else:
            best_version = max(valid_versions, key=lambda x: x['metrics'][metric])
        
        return self.load_model(model_type, best_version['version'])
    
    def _update_latest_link(self, model_dir, version):
        latest_link = os.path.join(model_dir, 'latest.txt')
        with open(latest_link, 'w') as f:
            f.write(version)
    
    def delete_model(self, model_type, version):
        model_dir = os.path.join(self.models_dir, model_type)
        model_path = os.path.join(model_dir, f'{version}.pkl')
        metadata_path = os.path.join(model_dir, f'{version}_metadata.json')
        
        if os.path.exists(model_path):
            os.remove(model_path)
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        
        logger.info(f"Model deleted: {model_type} {version}")
