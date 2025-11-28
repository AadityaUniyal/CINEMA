#!/usr/bin/env python3
Initialize database with CSV data
Run this script once to load all CSV files into MongoDB

from data_loader import DataLoader
import sys

def main():
    print("=" * 60)
    print("MovieLens Database Initialization")
    print("=" * 60)
    print()
    
    try:
        loader = DataLoader()
        loader.load_csv_to_mongodb()
        
        if loader.verify_data():
            print("\n✅ Database initialized successfully!")
            print("\nYou can now start the Flask application:")
            print("  python app.py")
            return 0
        else:
            print("\n❌ Data verification failed!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
