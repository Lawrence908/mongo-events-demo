#!/usr/bin/env python3
"""
Test MongoDB Atlas connection directly
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_atlas_connection():
    """Test direct connection to MongoDB Atlas"""
    print("🔌 Testing MongoDB Atlas Connection...")
    
    # Get connection details
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
        
        # Test checkins collection
        checkins = database.checkins
        count = checkins.count_documents({})
        print(f"📊 Check-ins collection has {count} documents")
        
        # Test creating a sample check-in with proper types
        from bson import ObjectId
        from datetime import datetime
        
        sample_checkin = {
            "event_id": ObjectId("507f1f77bcf86cd799439011"),
            "user_id": ObjectId("507f1f77bcf86cd799439012"),
            "venue_id": ObjectId("507f1f77bcf86cd799439013"),
            "qr_code": "TEST_QR_123",
            "check_in_time": datetime.now(),
            "created_at": datetime.now()
        }
        
        result = checkins.insert_one(sample_checkin)
        print(f"✅ Successfully inserted test check-in with ID: {result.inserted_id}")
        
        # Clean up test data
        checkins.delete_one({"_id": result.inserted_id})
        print("🧹 Cleaned up test data")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_atlas_connection()
    if success:
        print("\n🎉 MongoDB Atlas connection test successful!")
    else:
        print("\n💥 MongoDB Atlas connection test failed!")
