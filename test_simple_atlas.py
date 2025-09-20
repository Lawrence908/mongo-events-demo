#!/usr/bin/env python3
"""
Simple MongoDB Atlas connection test
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_simple_connection():
    """Test basic connection to MongoDB Atlas"""
    print("🔌 Testing MongoDB Atlas Connection...")
    
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME")
    
    print(f"URI: {uri}")
    print(f"Database: {db_name}")
    
    try:
        # Connect to MongoDB Atlas
        client = MongoClient(uri)
        database = client[db_name]
        
        # Test connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        # List collections
        collections = database.list_collection_names()
        print(f"📁 Available collections: {collections}")
        
        # Test basic operations for each collection
        collections_to_test = ['events', 'venues', 'users', 'checkins', 'reviews']
        for collection_name in collections_to_test:
            if collection_name in collections:
                collection = database[collection_name]
                count = collection.count_documents({})
                print(f"📊 {collection_name.capitalize()} collection has {count} documents")
                
                # Test a simple query
                result = list(collection.find().limit(1))
                print(f"🔍 {collection_name.capitalize()} sample query returned {len(result)} documents")
            else:
                print(f"⚠️  {collection_name.capitalize()} collection not found")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_connection()
    if success:
        print("\n🎉 MongoDB Atlas connection test successful!")
        print("✅ Ready for enhanced check-ins testing!")
    else:
        print("\n💥 MongoDB Atlas connection test failed!")
