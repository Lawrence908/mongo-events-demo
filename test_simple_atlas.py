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
        
        # Test basic operations
        checkins = database.checkins
        count = checkins.count_documents({})
        print(f"📊 Check-ins collection has {count} documents")
        
        # Test a simple query
        result = list(checkins.find().limit(1))
        print(f"🔍 Sample query returned {len(result)} documents")
        
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
