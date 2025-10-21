#!/usr/bin/env python3
"""
Comprehensive MongoDB Atlas connection test for all collections
Tests check-ins, reviews, events, venues, and users collections
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

def test_comprehensive_atlas_connection():
    """Test comprehensive connection to MongoDB Atlas with all collections"""
    print("🔌 Testing Comprehensive MongoDB Atlas Connection...")
    print("=" * 60)
    
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME")
    
    print(f"URI: {uri}")
    print(f"Database: {db_name}")
    print()
    
    try:
        # Connect to MongoDB Atlas
        client = MongoClient(uri)
        database = client[db_name]
        
        # Test connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        print()
        
        # List all collections
        collections = database.list_collection_names()
        print(f"📁 Available collections: {collections}")
        print()
        
        # Test each collection
        collections_to_test = {
            'events': {
                'description': 'Event management with geospatial support',
                'sample_doc': {
                    "title": "Test Event",
                    "category": "Technology",
                    "location": {
                        "type": "Point",
                        "coordinates": [-74.0060, 40.7128]
                    },
                    "startDate": datetime.now(timezone.utc),
                    "createdAt": datetime.now(timezone.utc),
                    "updatedAt": datetime.now(timezone.utc)
                }
            },
            'venues': {
                'description': 'Venue information with location data',
                'sample_doc': {
                    "name": "Test Venue",
                    "location": {
                        "type": "Point",
                        "coordinates": [-74.0060, 40.7128]
                    },
                    "address": {
                        "street": "123 Test St",
                        "city": "New York",
                        "state": "NY",
                        "zip": "10001",
                        "country": "USA"
                    },
                    "createdAt": datetime.now(timezone.utc)
                }
            },
            'users': {
                'description': 'User profiles and preferences',
                'sample_doc': {
                    "email": "test@example.com",
                    "profile": {
                        "first_name": "Test",
                        "last_name": "User"
                    },
                    "createdAt": datetime.now(timezone.utc)
                }
            },
            'checkins': {
                'description': 'Enhanced check-ins bridge table with analytics',
                'sample_doc': {
                    "eventId": ObjectId("507f1f77bcf86cd799439011"),
                    "userId": ObjectId("507f1f77bcf86cd799439012"),
                    "venueId": ObjectId("507f1f77bcf86cd799439013"),
                    "qrCode": "TEST_QR_123",
                    "checkInMethod": "qrCode",
                    "ticketTier": "VIP",
                    "checkInTime": datetime.now(timezone.utc),
                    "createdAt": datetime.now(timezone.utc),
                    "metadata": {
                        "device_info": "iPhone 13 Pro",
                        "ip_address": "192.168.1.100",
                        "staff_verified": True
                    }
                }
            },
            'reviews': {
                'description': 'User reviews for events and venues',
                'sample_doc': {
                    "eventId": ObjectId("507f1f77bcf86cd799439011"),
                    "userId": ObjectId("507f1f77bcf86cd799439012"),
                    "rating": 5,
                    "comment": "Great event! Highly recommended.",
                    "createdAt": datetime.now(timezone.utc),
                    "updatedAt": datetime.now(timezone.utc)
                }
            }
        }
        
        test_results = {}
        
        for collection_name, config in collections_to_test.items():
            print(f"🧪 Testing {collection_name.capitalize()} collection...")
            print(f"   Description: {config['description']}")
            
            if collection_name in collections:
                collection = database[collection_name]
                
                # Count existing documents
                count = collection.count_documents({})
                print(f"   📊 Current document count: {count}")
                
                # Test basic query
                sample_docs = list(collection.find().limit(1))
                print(f"   🔍 Sample query returned {len(sample_docs)} documents")
                
                # Test inserting sample document
                try:
                    result = collection.insert_one(config['sample_doc'])
                    print(f"   ✅ Successfully inserted test document with ID: {result.inserted_id}")
                    
                    # Clean up test data
                    collection.delete_one({"_id": result.inserted_id})
                    print(f"   🧹 Cleaned up test data")
                    
                    test_results[collection_name] = "PASSED"
                    
                except Exception as e:
                    print(f"   ❌ Failed to insert test document: {e}")
                    test_results[collection_name] = f"FAILED: {str(e)}"
                    
            else:
                print(f"   ⚠️  Collection not found")
                test_results[collection_name] = "NOT_FOUND"
            
            print()
        
        # Test cross-collection relationships
        print("🔗 Testing cross-collection relationships...")
        
        # Test check-ins with venue denormalization
        if 'checkins' in collections and 'venues' in collections:
            print("   Testing check-ins venue denormalization...")
            checkins = database.checkins
            venues = database.venues
            
            # Count check-ins with venue references
            venue_checkins = checkins.count_documents({"venueId": {"$exists": True}})
            print(f"   📊 Check-ins with venue references: {venue_checkins}")
            
            # Count venues with check-ins
            venue_ids = list(checkins.distinct("venueId"))
            venues_with_checkins = venues.count_documents({"_id": {"$in": venue_ids}})
            print(f"   📊 Venues with check-ins: {venues_with_checkins}")
        
        # Test reviews targeting
        if 'reviews' in collections:
            print("   Testing reviews targeting...")
            reviews = database.reviews
            
            event_reviews = reviews.count_documents({"eventId": {"$exists": True}})
            venue_reviews = reviews.count_documents({"venueId": {"$exists": True}})
            print(f"   📊 Event reviews: {event_reviews}")
            print(f"   📊 Venue reviews: {venue_reviews}")
        
        print()
        
        # Summary
        print("📋 Test Results Summary:")
        print("=" * 40)
        for collection_name, result in test_results.items():
            status_icon = "✅" if result == "PASSED" else "❌" if "FAILED" in result else "⚠️"
            print(f"{status_icon} {collection_name.capitalize()}: {result}")
        
        # Check if all critical collections are working
        critical_collections = ['events', 'venues', 'users', 'checkins', 'reviews']
        all_passed = all(test_results.get(col) == "PASSED" for col in critical_collections)
        
        print()
        if all_passed:
            print("🎉 All collections are working correctly!")
            print("✅ Enhanced check-ins and reviews functionality ready!")
        else:
            print("⚠️  Some collections have issues - check the results above")
        
        client.close()
        return all_passed
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_comprehensive_atlas_connection()
    if success:
        print("\n🚀 MongoDB Atlas comprehensive test successful!")
        print("🎯 Ready for full application testing!")
    else:
        print("\n💥 MongoDB Atlas comprehensive test failed!")
