from config import Config
import certifi
from pymongo import MongoClient

print('Testing MongoDB connection...')
print(f'Using URI: {Config.MONGO_URI[:50]}...')
try:
    # Connect using certifi CA bundle for proper TLS validation
    client = MongoClient(
        Config.MONGO_URI,
        serverSelectionTimeoutMS=10000,
        tls=True,
        tlsCAFile=certifi.where()
    )
    info = client.server_info()
    print('✅ Connected successfully!')
    print('Server info:')
    print(f"  MongoDB version: {info.get('version')}")
    print(f"  Server: {info.get('ok')}")
    
    # Test database access
    db = client[Config.DB_NAME]
    collections = db.list_collection_names()
    print(f"\nDatabase '{Config.DB_NAME}' collections: {collections}")
    
except Exception as e:
    print('❌ Connection failed:')
    print(f'Error: {e}')
    print('\nTroubleshooting tips:')
    print('1. Check your MongoDB Atlas IP whitelist (add 0.0.0.0/0 for testing)')
    print('2. Verify credentials in config.py')
    print('3. Ensure cluster is running in MongoDB Atlas')
