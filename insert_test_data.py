#!/usr/bin/env python3
"""
Simple script to insert test data for map visualization testing
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pymongo import MongoClient

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Load the generated test data
with open('map_test_events.json', 'r') as f:
    events_data = json.load(f)

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'eventdb')

def insert_test_data():
    """Insert test data into MongoDB"""
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        
        print(f"Connecting to MongoDB: {MONGODB_URI}")
        print(f"Using database: {DB_NAME}")
        
        # Clear existing events
        print("Clearing existing events...")
        db.events.drop()
        
        # Convert string dates back to datetime objects
        for event in events_data:
            event['start_date'] = datetime.fromisoformat(event['start_date'])
            event['end_date'] = datetime.fromisoformat(event['end_date'])
            event['created_at'] = datetime.fromisoformat(event['created_at'])
            event['updated_at'] = datetime.fromisoformat(event['updated_at'])
        
        # Insert events
        print(f"Inserting {len(events_data)} events...")
        result = db.events.insert_many(events_data)
        print(f"✅ Inserted {len(result.inserted_ids)} events")
        
        # Create geospatial index
        print("Creating geospatial index...")
        db.events.create_index([("location", "2dsphere")])
        print("✅ Geospatial index created")
        
        # Verify data
        count = db.events.count_documents({})
        print(f"✅ Total events in database: {count}")
        
        # Test a nearby query
        print("\nTesting nearby events query...")
        test_query = db.events.aggregate([
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [-74.0060, 40.7128]  # NYC
                    },
                    "distanceField": "distance",
                    "maxDistance": 50000,  # 50km
                    "spherical": True
                }
            },
            {"$limit": 5}
        ])
        
        nearby_events = list(test_query)
        print(f"✅ Found {len(nearby_events)} events near NYC")
        
        if nearby_events:
            print("Sample event:")
            sample = nearby_events[0]
            print(f"  Title: {sample['title']}")
            print(f"  Category: {sample['category']}")
            print(f"  Distance: {sample.get('distance', 'N/A')} meters")
        
        print("\n🎉 Test data insertion complete!")
        print("You can now test the map page at: http://localhost:5001/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = insert_test_data()
    sys.exit(0 if success else 1)
