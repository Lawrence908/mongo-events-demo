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
        
        # Test all collections
        collections_to_test = ['events', 'venues', 'users', 'checkins', 'reviews']
        for collection_name in collections_to_test:
            if collection_name in collections:
                collection = database[collection_name]
                count = collection.count_documents({})
                print(f"📊 {collection_name.capitalize()} collection has {count} documents")
            else:
                print(f"⚠️  {collection_name.capitalize()} collection not found")
        
        # Test creating a sample check-in with proper types
        from bson import ObjectId
        from datetime import datetime
        
        print("\n🧪 Testing check-ins collection...")
        checkins = database.checkins
        sample_checkin = {
            "eventId": ObjectId("507f1f77bcf86cd799439011"),
            "userId": ObjectId("507f1f77bcf86cd799439012"),
            "venueId": ObjectId("507f1f77bcf86cd799439013"),
            "qrCode": "TEST_QR_123",
            "checkInTime": datetime.now(),
            "createdAt": datetime.now()
        }
        
        result = checkins.insert_one(sample_checkin)
        print(f"✅ Successfully inserted test check-in with ID: {result.inserted_id}")
        
        # Clean up test data
        checkins.delete_one({"_id": result.inserted_id})
        print("🧹 Cleaned up check-in test data")
        
        # Test creating a sample review with proper types
        print("\n🧪 Testing reviews collection...")
        reviews = database.reviews
        sample_review = {
            "eventId": ObjectId("507f1f77bcf86cd799439011"),
            "userId": ObjectId("507f1f77bcf86cd799439012"),
            "rating": 5,
            "comment": "Great event!",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        result = reviews.insert_one(sample_review)
        print(f"✅ Successfully inserted test review with ID: {result.inserted_id}")
        
        # Clean up test data
        reviews.delete_one({"_id": result.inserted_id})
        print("🧹 Cleaned up review test data")
        
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
