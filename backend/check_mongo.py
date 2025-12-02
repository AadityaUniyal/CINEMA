from config import Config
import certifi
from pymongo import MongoClient

print('Testing MongoDB connection...')
try:
    client = MongoClient(
        Config.MONGO_URI,
        serverSelectionTimeoutMS=5000,
        tls=True,
        tlsCAFile=certifi.where()
    )
    info = client.server_info()
    print('Connected. Server info:')
    print(info)
except Exception as e:
    print('Connection failed:')
    print(e)
