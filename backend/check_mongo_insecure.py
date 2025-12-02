from config import Config
import ssl
from pymongo import MongoClient

print('Testing MongoDB connection with tlsAllowInvalidCertificates=True (diagnostic only)')
try:
    client = MongoClient(
        Config.MONGO_URI,
        serverSelectionTimeoutMS=5000,
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    info = client.server_info()
    print('Connected (insecure). Server info:')
    print(info)
except Exception as e:
    print('Connection failed:')
    print(e)
