import pandas as pd
from pymongo import MongoClient
from config import Config
import os

class DataLoader:
    
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
    
    def load_csv_to_mongodb(self):
        print("Starting data import to MongoDB...")
        
        if os.path.exists(f'{Config.DATA_DIR}/{Config.MOVIES_FILE}'):
            movies_df = pd.read_csv(f'{Config.DATA_DIR}/{Config.MOVIES_FILE}', nrows=20000)
            movies_df['genres_list'] = movies_df['genres'].str.split('|')
            movies_collection = self.db['movies']
            movies_collection.delete_many({})
            movies_collection.insert_many(movies_df.to_dict('records'))
            print(f"✓ Loaded {len(movies_df)} movies")
        
        if os.path.exists(f'{Config.DATA_DIR}/{Config.RATINGS_FILE}'):
            ratings_df = pd.read_csv(f'{Config.DATA_DIR}/{Config.RATINGS_FILE}', nrows=20000)
            ratings_collection = self.db['ratings']
            ratings_collection.delete_many({})
            
            batch_size = 10000
            for i in range(0, len(ratings_df), batch_size):
                batch = ratings_df.iloc[i:i+batch_size]
                ratings_collection.insert_many(batch.to_dict('records'))
                print(f"  Loaded {min(i+batch_size, len(ratings_df))}/{len(ratings_df)} ratings")
            print(f"✓ Loaded {len(ratings_df)} ratings")
        
        print("⚠️  Skipping tags and links (not essential for core features)")
        
        self.create_indexes()
        
        print("\n✅ Data import completed successfully!")
    
    def create_indexes(self):
        print("\nCreating indexes...")
        
        self.db['movies'].create_index('movieId')
        self.db['ratings'].create_index('userId')
        self.db['ratings'].create_index('movieId')
        self.db['ratings'].create_index([('userId', 1), ('movieId', 1)])
        
        print("✓ Indexes created")
    
    def verify_data(self):
        print("\nVerifying data...")
        
        movies_count = self.db['movies'].count_documents({})
        ratings_count = self.db['ratings'].count_documents({})
        
        print(f"Movies: {movies_count}")
        print(f"Ratings: {ratings_count}")
        
        return movies_count > 0 and ratings_count > 0

if __name__ == '__main__':
    loader = DataLoader()
    loader.load_csv_to_mongodb()
    loader.verify_data()
