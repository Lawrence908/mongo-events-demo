#!/usr/bin/env python3
"""
Test script for EVE-11: Nearby events GeoJSON API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services import get_event_service, EventsNearbyQuery
from app.database import get_mongodb
import json

def test_nearby_events_api():
    """Test the nearby events API implementation"""
    print("🧪 Testing EVE-11: Nearby events GeoJSON API")
    print("=" * 50)
    
    # Initialize database and service
    mongodb = get_mongodb()
    db = mongodb.database
    service = get_event_service()
    
    # Test 1: Check if we have any events in the database
    print("\n📄 Test 1: Check database for events")
    try:
        events_count = db.events.count_documents({})
        print(f"   Total events in database: {events_count}")
        
        if events_count == 0:
            print("   ⚠️  No events found. Creating test event...")
            # Create a test event
            from datetime import datetime
            test_event = {
                "title": "Test Music Event",
                "description": "A test event for geospatial testing",
                "category": "music",
                "location": {
                    "type": "Point",
                    "coordinates": [-74.0060, 40.7128]  # NYC coordinates
                },
                "start_date": datetime(2024, 12, 25, 20, 0, 0),
                "max_attendees": 100,
                "organizer": "Test Organizer",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = db.events.insert_one(test_event)
            print(f"   ✅ Created test event with ID: {result.inserted_id}")
            events_count = db.events.count_documents({})
            print(f"   Total events now: {events_count}")
    except Exception as e:
        print(f"   ❌ Error checking database: {e}")
        return False
    
    # Test 2: Test the nearby events service method
    print("\n📄 Test 2: Test nearby events service method")
    try:
        query = EventsNearbyQuery(
            longitude=-74.0060,  # NYC longitude
            latitude=40.7128,    # NYC latitude
            radius_km=10,        # 10km radius
            limit=10
        )
        
        result = service.get_events_nearby(query)
        print(f"   ✅ Service method executed successfully")
        print(f"   Result type: {type(result)}")
        print(f"   Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # Check GeoJSON structure
        if isinstance(result, dict):
            if result.get("type") == "FeatureCollection":
                print("   ✅ Returns valid GeoJSON FeatureCollection")
                features = result.get("features", [])
                print(f"   Features count: {len(features)}")
                
                if features:
                    feature = features[0]
                    print(f"   First feature type: {feature.get('type')}")
                    print(f"   First feature geometry: {feature.get('geometry')}")
                    print(f"   First feature properties: {feature.get('properties')}")
                    
                    # Check distance field
                    distance = feature.get('properties', {}).get('distance')
                    if distance is not None:
                        print(f"   ✅ Distance field present: {distance}")
                        if isinstance(distance, (int, float)):
                            print(f"   ✅ Distance is numeric: {distance}")
                            if len(str(distance).split('.')[-1]) <= 2:
                                print(f"   ✅ Distance rounded to 2 decimals: {distance}")
                            else:
                                print(f"   ⚠️  Distance not properly rounded: {distance}")
                        else:
                            print(f"   ❌ Distance is not numeric: {distance}")
                    else:
                        print(f"   ❌ Distance field missing")
                else:
                    print("   ⚠️  No features returned")
            else:
                print(f"   ❌ Not a FeatureCollection: {result.get('type')}")
        else:
            print(f"   ❌ Result is not a dictionary: {type(result)}")
            
    except Exception as e:
        print(f"   ❌ Error testing service method: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Test with different parameters
    print("\n📄 Test 3: Test with different parameters")
    try:
        query = EventsNearbyQuery(
            longitude=-74.0060,
            latitude=40.7128,
            radius_km=1,  # Smaller radius
            limit=5
        )
        
        result = service.get_events_nearby(query)
        features = result.get("features", [])
        print(f"   ✅ Smaller radius test: {len(features)} features")
        
    except Exception as e:
        print(f"   ❌ Error testing with different parameters: {e}")
        return False
    
    print("\n✅ All tests completed!")
    return True

if __name__ == "__main__":
    success = test_nearby_events_api()
    sys.exit(0 if success else 1)
