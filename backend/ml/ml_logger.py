import logging
import os
from datetime import datetime

log_dir = 'logs/ml'
os.makedirs(log_dir, exist_ok=True)

def get_ml_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        fh = logging.FileHandler(f'{log_dir}/ml_{datetime.now().strftime("%Y%m%d")}.log')
        fh.setLevel(logging.INFO)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger
