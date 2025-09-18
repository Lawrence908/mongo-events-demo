#!/usr/bin/env python3
"""
Performance Testing Script for MongoDB Events Demo
Tests query performance with different indexes and data volumes
"""

import time
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.database import get_mongodb
from app.services import get_event_service
from app.models import EventCreate, EventLocation

def generate_test_events(count: int = 1000) -> List[Dict[str, Any]]:
    """Generate test events for performance testing"""
    events = []
    categories = ["Technology", "Music", "Sports", "Food & Drink", "Arts & Culture"]
    
    # Major cities for geospatial testing
    cities = [
        {"lat": 40.7128, "lng": -74.0060, "name": "New York"},
        {"lat": 34.0522, "lng": -118.2437, "name": "Los Angeles"},
        {"lat": 41.8781, "lng": -87.6298, "name": "Chicago"},
        {"lat": 29.7604, "lng": -95.3698, "name": "Houston"},
        {"lat": 33.4484, "lng": -112.0740, "name": "Phoenix"},
    ]
    
    for i in range(count):
        city = random.choice(cities)
        # Add some random variation to coordinates
        lat = city["lat"] + random.uniform(-0.1, 0.1)
        lng = city["lng"] + random.uniform(-0.1, 0.1)
        
        # Generate dates from 1 month ago to 3 months in the future
        start_date = datetime.utcnow() + timedelta(
            days=random.randint(-30, 90),
            hours=random.randint(0, 23)
        )
        end_date = start_date + timedelta(hours=random.randint(1, 8))
        
        event = {
            "title": f"Test Event {i+1}",
            "description": f"Description for test event {i+1}",
            "category": random.choice(categories),
            "location": {
                "type": "Point",
                "coordinates": [lng, lat]
            },
            "start_date": start_date,
            "end_date": end_date,
            "organizer": f"Organizer {i+1}",
            "max_attendees": random.randint(10, 500),
            "tags": [f"tag{i%10}", f"category{random.randint(1,5)}"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        events.append(event)
    
    return events

def test_query_performance():
    """Test various query patterns and measure performance"""
    db = get_mongodb()
    service = get_event_service()
    
    print("🚀 MongoDB Events Demo - Performance Testing")
    print("=" * 50)
    
    # Clear existing test data
    print("🧹 Clearing existing test data...")
    db.events.delete_many({"title": {"$regex": "^Test Event"}})
    
    # Generate and insert test data
    print("📝 Generating test data...")
    test_events = generate_test_events(5000)  # 5,000 test events
    
    print(f"💾 Inserting {len(test_events)} test events...")
    start_time = time.time()
    db.events.insert_many(test_events)
    insert_time = time.time() - start_time
    print(f"✅ Inserted in {insert_time:.2f} seconds ({len(test_events)/insert_time:.0f} events/sec)")
    
    # Test 1: Basic text search
    print("\n🔍 Test 1: Text Search Performance")
    start_time = time.time()
    results = service.get_events(search="Technology", limit=100)
    search_time = time.time() - start_time
    print(f"   Text search: {search_time:.3f}s ({len(results.get('events', []))} results)")
    
    # Test 2: Category filtering
    print("\n🏷️ Test 2: Category Filtering Performance")
    start_time = time.time()
    results = service.get_events(category="Technology", limit=100)
    category_time = time.time() - start_time
    print(f"   Category filter: {category_time:.3f}s ({len(results.get('events', []))} results)")
    
    # Test 3: Geospatial query
    print("\n🌍 Test 3: Geospatial Query Performance")
    start_time = time.time()
    geojson = service.get_events_nearby({
        "longitude": -74.0060,  # NYC
        "latitude": 40.7128,
        "radius_km": 50,
        "limit": 100
    })
    geo_time = time.time() - start_time
    print(f"   Geospatial query: {geo_time:.3f}s ({len(geojson.get('features', []))} results)")
    
    # Test 4: Weekend events query
    print("\n📅 Test 4: Weekend Events Query Performance")
    start_time = time.time()
    weekend_events = service.get_events_this_weekend(-74.0060, 40.7128, 50)
    weekend_time = time.time() - start_time
    print(f"   Weekend events: {weekend_time:.3f}s ({weekend_events.get('total_events', 0)} results)")
    
    # Test 5: Date range query
    print("\n📊 Test 5: Date Range Query Performance")
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=30)
    start_time = time.time()
    date_events = service.get_events_by_date_range(start_date, end_date, "Technology")
    date_time = time.time() - start_time
    print(f"   Date range query: {date_time:.3f}s ({len(date_events)} results)")
    
    # Test 6: Analytics aggregation
    print("\n📈 Test 6: Analytics Aggregation Performance")
    start_time = time.time()
    analytics = service.get_analytics()
    analytics_time = time.time() - start_time
    print(f"   Analytics query: {analytics_time:.3f}s")
    print(f"   Total events: {analytics.get('total_events', 0)}")
    print(f"   Upcoming events: {analytics.get('upcoming_events', 0)}")
    
    # Test 7: Cursor-based pagination
    print("\n📄 Test 7: Cursor-based Pagination Performance")
    start_time = time.time()
    page1 = service.get_events(limit=50, cursor_id=None)
    cursor_time = time.time() - start_time
    print(f"   First page: {cursor_time:.3f}s ({len(page1.get('events', []))} results)")
    
    if page1.get('next_cursor'):
        start_time = time.time()
        page2 = service.get_events(limit=50, cursor_id=page1['next_cursor'])
        cursor_time2 = time.time() - start_time
        print(f"   Second page: {cursor_time2:.3f}s ({len(page2.get('events', []))} results)")
    
    # Test 8: Index usage analysis
    print("\n🔧 Test 8: Index Usage Analysis")
    try:
        # Explain a sample query
        explain_result = db.events.find({"category": "Technology"}).explain()
        execution_stats = explain_result.get('executionStats', {})
        print(f"   Index used: {execution_stats.get('totalKeysExamined', 0)} keys examined")
        print(f"   Documents examined: {execution_stats.get('totalDocsExamined', 0)}")
        print(f"   Execution time: {execution_stats.get('executionTimeMillis', 0)}ms")
    except Exception as e:
        print(f"   Explain failed: {e}")
    
    # Performance summary
    print("\n📊 Performance Summary")
    print("=" * 30)
    print(f"Insert Performance: {len(test_events)/insert_time:.0f} events/sec")
    print(f"Text Search: {search_time:.3f}s")
    print(f"Category Filter: {category_time:.3f}s")
    print(f"Geospatial Query: {geo_time:.3f}s")
    print(f"Weekend Events: {weekend_time:.3f}s")
    print(f"Date Range: {date_time:.3f}s")
    print(f"Analytics: {analytics_time:.3f}s")
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    db.events.delete_many({"title": {"$regex": "^Test Event"}})
    print("✅ Test data cleaned up")

def test_index_effectiveness():
    """Test the effectiveness of different indexes"""
    db = get_mongodb()
    
    print("\n🔍 Index Effectiveness Analysis")
    print("=" * 40)
    
    # List all indexes
    indexes = list(db.events.list_indexes())
    print(f"Total indexes: {len(indexes)}")
    for index in indexes:
        print(f"  - {index['name']}: {index['key']}")
    
    # Test compound index usage
    print("\nTesting compound index usage...")
    try:
        # This should use the compound index (category, start_date)
        explain_result = db.events.find({
            "category": "Technology",
            "start_date": {"$gte": datetime.utcnow()}
        }).sort("start_date", 1).explain()
        
        execution_stats = explain_result.get('executionStats', {})
        print(f"Compound query execution time: {execution_stats.get('executionTimeMillis', 0)}ms")
        print(f"Index used: {execution_stats.get('totalKeysExamined', 0)} keys examined")
        
    except Exception as e:
        print(f"Compound index test failed: {e}")

if __name__ == "__main__":
    test_query_performance()
    test_index_effectiveness()
    print("\n🎉 Performance testing complete!")
