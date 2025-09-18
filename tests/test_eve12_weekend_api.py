#!/usr/bin/env python3
"""
Test script for EVE-12: Weekend Near-Me Discovery API

Tests the weekend events API that combines geospatial queries with weekend date filtering.
"""
import sys
import os
import unittest
import time
from datetime import datetime, timedelta
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services import get_event_service, EventService
from app.database import get_mongodb
from app.utils import calculate_weekend_window
from app.models import EventCreate


class TestWeekendAPI(unittest.TestCase):
    """Test cases for EVE-12: Weekend Near-Me Discovery API"""
    
    def setUp(self):
        """Set up test environment"""
        self.mongodb = get_mongodb()
        self.db = self.mongodb.database
        self.service = get_event_service()
        
        # Ensure database and indexes are properly initialized
        self.mongodb._create_indexes()
        
        # Clean up any existing test events (more comprehensive cleanup)
        self.db.events.delete_many({"title": {"$regex": "^Test Weekend"}})
        self.db.events.delete_many({"title": {"$regex": "^Test Event"}})
        self.db.events.delete_many({"organizer": "Test Organizer"})
        
        # Get current weekend range for testing
        self.friday, self.sunday = calculate_weekend_window()
        
    def tearDown(self):
        """Clean up test data"""
        self.db.events.delete_many({"title": {"$regex": "^Test Weekend"}})
        self.db.events.delete_many({"title": {"$regex": "^Test Event"}})
        self.db.events.delete_many({"organizer": "Test Organizer"})
    
    def _clean_test_events(self):
        """Clean up all test events"""
        self.db.events.delete_many({"title": {"$regex": "^Test"}})
        self.db.events.delete_many({"organizer": "Test Organizer"})
        self.db.events.delete_many({"organizer": "Music Organizer"})
    
    def _ensure_geospatial_index(self):
        """Ensure geospatial index exists for testing"""
        try:
            # Check if geospatial index exists
            indexes = list(self.db.events.list_indexes())
            has_geo_index = any(
                'location' in str(index.get('key', {})) and '2dsphere' in str(index.get('key', {}))
                for index in indexes
            )
            
            if not has_geo_index:
                # Create geospatial index if it doesn't exist
                from pymongo import GEOSPHERE
                self.db.events.create_index([("location", GEOSPHERE)], name="location_2dsphere")
        except Exception as e:
            print(f"Warning: Could not ensure geospatial index: {e}")
    
    def test_weekend_api_basic_functionality(self):
        """Test basic weekend API functionality"""
        print("\n🧪 Test 1: Basic Weekend API Functionality")
        
        # Ensure clean state and geospatial index
        self._clean_test_events()
        self._ensure_geospatial_index()
        
        # Test with no events (should return empty result)
        result = self.service.get_events_this_weekend(-74.0060, 40.7128, 50)
        
        # Verify response structure
        self.assertIn("type", result)
        self.assertIn("features", result)
        self.assertIn("weekend_range", result)
        self.assertEqual(result["type"], "FeatureCollection")
        self.assertIsInstance(result["features"], list)
        self.assertEqual(len(result["features"]), 0)
        
        print("   ✅ Empty result structure is correct")
    
    def test_weekend_api_with_test_events(self):
        """Test weekend API with test events"""
        print("\n🧪 Test 2: Weekend API with Test Events")
        
        # Ensure clean state and geospatial index
        self._clean_test_events()
        self._ensure_geospatial_index()
        
        # Create test events for this weekend
        test_events = [
            {
                "title": "Test Weekend Event 1",
                "description": "Saturday evening event",
                "category": "Technology",
                "location": {"type": "Point", "coordinates": [-74.0060, 40.7128]},
                "start_date": self.friday + timedelta(hours=2),  # Saturday 8pm
                "end_date": self.friday + timedelta(hours=4),    # Saturday 10pm
                "max_attendees": 100,
                "organizer": "Test Organizer",
                "tags": ["test", "weekend", "tech"]
            },
            {
                "title": "Test Weekend Event 2", 
                "description": "Sunday morning event",
                "category": "Music",
                "location": {"type": "Point", "coordinates": [-74.0050, 40.7130]},  # Slightly different location
                "start_date": self.sunday - timedelta(hours=6),  # Sunday 6pm
                "end_date": self.sunday - timedelta(hours=4),    # Sunday 8pm
                "max_attendees": 50,
                "organizer": "Music Organizer",
                "tags": ["test", "weekend", "music"]
            }
        ]
        
        # Insert test events
        for event_data in test_events:
            event = EventCreate(**event_data)
            created_event = self.service.create_event(event)
            print(f"   ✅ Created event: {created_event.title}")
        
        # Test weekend API
        result = self.service.get_events_this_weekend(-74.0060, 40.7128, 50)
        
        # Verify results
        self.assertEqual(len(result["features"]), 2)
        self.assertEqual(result["total_events"], 2)
        
        # Verify GeoJSON structure
        for feature in result["features"]:
            self.assertIn("type", feature)
            self.assertIn("geometry", feature)
            self.assertIn("properties", feature)
            self.assertEqual(feature["type"], "Feature")
            self.assertEqual(feature["geometry"]["type"], "Point")
            self.assertIn("coordinates", feature["geometry"])
            
            # Verify properties
            props = feature["properties"]
            self.assertIn("id", props)
            self.assertIn("title", props)
            self.assertIn("category", props)
            self.assertIn("start_date", props)
            self.assertIn("distance", props)
            self.assertIn("tags", props)
        
        print("   ✅ Weekend API returns correct GeoJSON structure")
        print(f"   ✅ Found {len(result['features'])} weekend events")
    
    def test_weekend_api_geospatial_filtering(self):
        """Test geospatial filtering in weekend API"""
        print("\n🧪 Test 3: Geospatial Filtering")
        
        # Ensure clean state and geospatial index
        self._clean_test_events()
        self._ensure_geospatial_index()
        
        # Create events at different distances
        events_data = [
            {
                "title": "Test Weekend Event - Close",
                "description": "Event within radius",
                "category": "Technology",
                "location": {"type": "Point", "coordinates": [-74.0060, 40.7128]},  # NYC
                "start_date": self.friday + timedelta(hours=2),
                "end_date": self.friday + timedelta(hours=4),
                "max_attendees": 100,
                "organizer": "Test Organizer",
                "tags": ["test", "close"]
            },
            {
                "title": "Test Weekend Event - Far",
                "description": "Event outside radius",
                "category": "Technology", 
                "location": {"type": "Point", "coordinates": [-80.0000, 40.0000]},  # Far from NYC
                "start_date": self.friday + timedelta(hours=2),
                "end_date": self.friday + timedelta(hours=4),
                "max_attendees": 100,
                "organizer": "Test Organizer",
                "tags": ["test", "far"]
            }
        ]
        
        # Insert test events
        for event_data in events_data:
            event = EventCreate(**event_data)
            self.service.create_event(event)
        
        # Test with small radius (should only find close event)
        result_close = self.service.get_events_this_weekend(-74.0060, 40.7128, 10)
        self.assertEqual(len(result_close["features"]), 1)
        self.assertEqual(result_close["features"][0]["properties"]["title"], "Test Weekend Event - Close")
        
        # Test with large radius (should find both events)
        result_far = self.service.get_events_this_weekend(-74.0060, 40.7128, 1000)
        self.assertEqual(len(result_far["features"]), 2)
        
        print("   ✅ Geospatial filtering works correctly")
        print(f"   ✅ Small radius: {len(result_close['features'])} events")
        print(f"   ✅ Large radius: {len(result_far['features'])} events")
    
    def test_weekend_api_temporal_filtering(self):
        """Test temporal filtering (weekend date range) in weekend API"""
        print("\n🧪 Test 4: Temporal Filtering")
        
        # Ensure clean state and geospatial index
        self._clean_test_events()
        self._ensure_geospatial_index()
        
        # Create events at different times
        events_data = [
            {
                "title": "Test Weekend Event - Friday",
                "description": "Event on Friday evening",
                "category": "Technology",
                "location": {"type": "Point", "coordinates": [-74.0060, 40.7128]},
                "start_date": self.friday + timedelta(hours=1),  # Friday 7pm
                "end_date": self.friday + timedelta(hours=3),    # Friday 9pm
                "max_attendees": 100,
                "organizer": "Test Organizer",
                "tags": ["test", "friday"]
            },
            {
                "title": "Test Weekend Event - Saturday",
                "description": "Event on Saturday",
                "category": "Technology",
                "location": {"type": "Point", "coordinates": [-74.0060, 40.7128]},
                "start_date": self.friday + timedelta(hours=25),  # Saturday 7pm
                "end_date": self.friday + timedelta(hours=27),    # Saturday 9pm
                "max_attendees": 100,
                "organizer": "Test Organizer",
                "tags": ["test", "saturday"]
            },
            {
                "title": "Test Weekend Event - Monday",
                "description": "Event on Monday (not weekend)",
                "category": "Technology",
                "location": {"type": "Point", "coordinates": [-74.0060, 40.7128]},
                "start_date": self.sunday + timedelta(hours=2),  # Monday 2am
                "end_date": self.sunday + timedelta(hours=4),    # Monday 4am
                "max_attendees": 100,
                "organizer": "Test Organizer",
                "tags": ["test", "monday"]
            }
        ]
        
        # Insert test events
        for event_data in events_data:
            event = EventCreate(**event_data)
            self.service.create_event(event)
        
        # Test weekend API (should only find Friday and Saturday events)
        result = self.service.get_events_this_weekend(-74.0060, 40.7128, 50)
        
        # Should find 2 events (Friday and Saturday, not Monday)
        self.assertEqual(len(result["features"]), 2)
        
        # Verify correct events are returned
        event_titles = [feature["properties"]["title"] for feature in result["features"]]
        self.assertIn("Test Weekend Event - Friday", event_titles)
        self.assertIn("Test Weekend Event - Saturday", event_titles)
        self.assertNotIn("Test Weekend Event - Monday", event_titles)
        
        print("   ✅ Temporal filtering works correctly")
        print(f"   ✅ Found {len(result['features'])} weekend events (excluded Monday event)")
    
    def test_weekend_api_performance(self):
        """Test weekend API performance"""
        print("\n🧪 Test 5: Performance Testing")
        
        # Ensure clean state and geospatial index
        self._clean_test_events()
        self._ensure_geospatial_index()
        
        # Create multiple test events for performance testing
        test_events = []
        for i in range(10):
            event_data = {
                "title": f"Test Weekend Event {i}",
                "description": f"Performance test event {i}",
                "category": "Technology",
                "location": {
                    "type": "Point", 
                    "coordinates": [
                        -74.0060 + (i * 0.001),  # Slightly different longitude
                        40.7128 + (i * 0.001)    # Slightly different latitude
                    ]
                },
                "start_date": self.friday + timedelta(hours=2 + i),
                "end_date": self.friday + timedelta(hours=4 + i),
                "max_attendees": 100,
                "organizer": "Test Organizer",
                "tags": ["test", "performance"]
            }
            test_events.append(EventCreate(**event_data))
        
        # Insert test events
        for event in test_events:
            self.service.create_event(event)
        
        # Measure performance
        start_time = time.time()
        result = self.service.get_events_this_weekend(-74.0060, 40.7128, 50)
        end_time = time.time()
        
        latency_ms = (end_time - start_time) * 1000
        
        # Verify performance is within acceptable limits
        self.assertLess(latency_ms, 200, f"Latency {latency_ms:.2f}ms exceeds 200ms target")
        self.assertEqual(len(result["features"]), 10)
        
        print(f"   ✅ Performance test passed: {latency_ms:.2f}ms")
        print(f"   ✅ Found {len(result['features'])} events")
    
    def test_weekend_api_response_structure(self):
        """Test weekend API response structure and data types"""
        print("\n🧪 Test 6: Response Structure Validation")
        
        # Ensure clean state and geospatial index
        self._clean_test_events()
        self._ensure_geospatial_index()
        
        # Create a test event
        event_data = {
            "title": "Test Weekend Event - Structure",
            "description": "Event for structure testing",
            "category": "Technology",
            "location": {"type": "Point", "coordinates": [-74.0060, 40.7128]},
            "start_date": self.friday + timedelta(hours=2),
            "end_date": self.friday + timedelta(hours=4),
            "max_attendees": 100,
            "organizer": "Test Organizer",
            "tags": ["test", "structure"]
        }
        
        event = EventCreate(**event_data)
        self.service.create_event(event)
        
        # Get weekend events
        result = self.service.get_events_this_weekend(-74.0060, 40.7128, 50)
        
        # Test top-level structure
        self.assertIn("type", result)
        self.assertIn("features", result)
        self.assertIn("weekend_range", result)
        self.assertIn("total_events", result)
        
        self.assertEqual(result["type"], "FeatureCollection")
        self.assertIsInstance(result["features"], list)
        self.assertIsInstance(result["total_events"], int)
        
        # Test weekend_range structure
        weekend_range = result["weekend_range"]
        self.assertIn("start", weekend_range)
        self.assertIn("end", weekend_range)
        
        # Test feature structure
        if result["features"]:
            feature = result["features"][0]
            self.assertIn("type", feature)
            self.assertIn("geometry", feature)
            self.assertIn("properties", feature)
            
            # Test geometry structure
            geometry = feature["geometry"]
            self.assertEqual(geometry["type"], "Point")
            self.assertIn("coordinates", geometry)
            self.assertIsInstance(geometry["coordinates"], list)
            self.assertEqual(len(geometry["coordinates"]), 2)
            
            # Test properties structure
            props = feature["properties"]
            required_props = ["id", "title", "description", "category", "start_date", "distance", "tags"]
            for prop in required_props:
                self.assertIn(prop, props)
            
            # Test data types
            self.assertIsInstance(props["id"], str)
            self.assertIsInstance(props["title"], str)
            self.assertIsInstance(props["category"], str)
            self.assertIsInstance(props["distance"], (int, float))
            self.assertIsInstance(props["tags"], list)
        
        print("   ✅ Response structure is valid")
        print("   ✅ All required fields present with correct types")
    
    def test_weekend_api_edge_cases(self):
        """Test edge cases for weekend API"""
        print("\n🧪 Test 7: Edge Cases")
        
        # Ensure clean state and geospatial index
        self._clean_test_events()
        self._ensure_geospatial_index()
        
        # Create a test event first to ensure the collection exists and has an index
        test_event = {
            "title": "Test Weekend Event - Edge Case",
            "description": "Event for edge case testing",
            "category": "Technology",
            "location": {"type": "Point", "coordinates": [-74.0060, 40.7128]},
            "start_date": self.friday + timedelta(hours=2),
            "end_date": self.friday + timedelta(hours=4),
            "max_attendees": 100,
            "organizer": "Test Organizer",
            "tags": ["test", "edge"]
        }
        
        event = EventCreate(**test_event)
        self.service.create_event(event)
        
        # Test with very small radius
        result_small = self.service.get_events_this_weekend(-74.0060, 40.7128, 0.001)
        self.assertIsInstance(result_small["features"], list)
        
        # Test with very large radius
        result_large = self.service.get_events_this_weekend(-74.0060, 40.7128, 10000)
        self.assertIsInstance(result_large["features"], list)
        
        # Test with coordinates at edge of valid range
        result_edge = self.service.get_events_this_weekend(180.0, 90.0, 50)
        self.assertIsInstance(result_edge["features"], list)
        
        print("   ✅ Edge cases handled correctly")
        print("   ✅ Small radius, large radius, and edge coordinates work")


def run_weekend_api_tests():
    """Run all weekend API tests"""
    print("🚀 EVE-12: Weekend Near-Me Discovery API Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWeekendAPI)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed! Weekend API is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = run_weekend_api_tests()
    sys.exit(0 if success else 1)
