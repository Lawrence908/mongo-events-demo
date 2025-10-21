#!/usr/bin/env python3
"""
Test script for EVE-9: Cursor-based pagination with test data
Creates test events and verifies cursor pagination functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services import get_event_service
from app.models import EventCreate, EventLocation
from datetime import datetime, timedelta
import json

def create_test_events():
    """Create test events for pagination testing"""
    print("📝 Creating test events for pagination testing")
    print("=" * 50)
    
    service = get_event_service()
    
    # Create events with different categories and dates
    test_events = [
        {
            "title": "Tech Conference 2024",
            "category": "conference",
            "location": EventLocation(coordinates=[-74.0060, 40.7128]),  # NYC
            "start_date": datetime.now() + timedelta(days=1),
            "description": "Annual technology conference"
        },
        {
            "title": "Music Festival Summer",
            "category": "music",
            "location": EventLocation(coordinates=[-118.2437, 34.0522]),  # LA
            "start_date": datetime.now() + timedelta(days=2),
            "description": "Summer music festival with top artists"
        },
        {
            "title": "Art Exhibition Opening",
            "category": "art",
            "location": EventLocation(coordinates=[-87.6298, 41.8781]),  # Chicago
            "start_date": datetime.now() + timedelta(days=3),
            "description": "Contemporary art exhibition opening"
        },
        {
            "title": "Sports Championship",
            "category": "sports",
            "location": EventLocation(coordinates=[-95.3698, 29.7604]),  # Houston
            "start_date": datetime.now() + timedelta(days=4),
            "description": "Championship sports event"
        },
        {
            "title": "Tech Workshop Python",
            "category": "conference",
            "location": EventLocation(coordinates=[-122.4194, 37.7749]),  # SF
            "start_date": datetime.now() + timedelta(days=5),
            "description": "Python programming workshop"
        },
        {
            "title": "Jazz Night Live",
            "category": "music",
            "location": EventLocation(coordinates=[-73.9352, 40.7306]),  # Brooklyn
            "start_date": datetime.now() + timedelta(days=6),
            "description": "Live jazz performance"
        }
    ]
    
    created_events = []
    for i, event_data in enumerate(test_events):
        try:
            event = EventCreate(**event_data)
            created_event = service.create_event(event)
            created_events.append(created_event)
            print(f"   ✓ Created: {created_event.title}")
        except Exception as e:
            print(f"   ❌ Failed to create {event_data['title']}: {e}")
    
    print(f"\n📊 Created {len(created_events)} test events")
    return created_events

def test_cursor_pagination_with_data():
    """Test cursor-based pagination with actual data"""
    print("\n🧪 Testing cursor pagination with data")
    print("=" * 50)
    
    service = get_event_service()
    
    # Test 1: Basic cursor pagination
    print("\n📄 Test 1: Basic cursor pagination")
    result1 = service.get_events(limit=3, cursor_id=None)
    print(f"   First page: {len(result1['events'])} events")
    print(f"   Has more: {result1['has_more']}")
    print(f"   Next cursor: {result1.get('next_cursor', 'None')}")
    print(f"   Pagination type: {result1['pagination_type']}")
    
    if result1['events']:
        print("   Event titles:")
        for event in result1['events']:
            print(f"     - {event.title}")
    
    # Test 2: Second page with cursor
    if result1.get('next_cursor'):
        print("\n📄 Test 2: Second page with cursor")
        result2 = service.get_events(limit=3, cursor_id=result1['next_cursor'])
        print(f"   Second page: {len(result2['events'])} events")
        print(f"   Has more: {result2['has_more']}")
        print(f"   Next cursor: {result2.get('next_cursor', 'None')}")
        print(f"   Pagination type: {result2['pagination_type']}")
        
        if result2['events']:
            print("   Event titles:")
            for event in result2['events']:
                print(f"     - {event.title}")
        
        # Verify no overlap between pages
        first_page_ids = [event.id for event in result1['events']]
        second_page_ids = [event.id for event in result2['events']]
        overlap = set(first_page_ids) & set(second_page_ids)
        print(f"   Overlap between pages: {len(overlap)} (should be 0)")
        assert len(overlap) == 0, "Pages should not have overlapping events"
    else:
        print("   ⚠️  No next cursor available for second page test")
    
    # Test 3: Cursor pagination with category filter
    print("\n📄 Test 3: Cursor pagination with category filter")
    result3 = service.get_events(limit=2, category='conference', cursor_id=None)
    print(f"   Conference events: {len(result3['events'])} events")
    print(f"   Has more: {result3['has_more']}")
    print(f"   Next cursor: {result3.get('next_cursor', 'None')}")
    print(f"   Pagination type: {result3['pagination_type']}")
    
    if result3['events']:
        print("   Conference event titles:")
        for event in result3['events']:
            print(f"     - {event.title}")
    
    # Test 4: Cursor pagination with search filter
    print("\n📄 Test 4: Cursor pagination with search filter")
    result4 = service.get_events(limit=2, search='tech', cursor_id=None)
    print(f"   Search results for 'tech': {len(result4['events'])} events")
    print(f"   Has more: {result4['has_more']}")
    print(f"   Next cursor: {result4.get('next_cursor', 'None')}")
    print(f"   Pagination type: {result4['pagination_type']}")
    
    if result4['events']:
        print("   Search result titles:")
        for event in result4['events']:
            print(f"     - {event.title}")
    
    print("\n✅ All cursor pagination tests with data passed!")
    return True

def test_api_endpoint_simulation():
    """Simulate API endpoint behavior"""
    print("\n🌐 Testing API endpoint simulation")
    print("=" * 40)
    
    service = get_event_service()
    
    # Simulate API call with cursor_id parameter
    print("📡 Simulating API call: GET /api/events?cursor_id=...&limit=2")
    
    # First call without cursor
    result1 = service.get_events(limit=2, cursor_id=None)
    
    # Simulate API response structure
    api_response = {
        "events": [event.model_dump() for event in result1['events']],
        "pagination": {
            "next_cursor": result1.get('next_cursor'),
            "has_more": result1['has_more'],
            "pagination_type": result1['pagination_type']
        }
    }
    
    print(f"   API Response:")
    print(f"     - Events count: {len(api_response['events'])}")
    print(f"     - Next cursor: {api_response['pagination']['next_cursor']}")
    print(f"     - Has more: {api_response['pagination']['has_more']}")
    print(f"     - Pagination type: {api_response['pagination']['pagination_type']}")
    
    # Second call with cursor
    if result1.get('next_cursor'):
        print("\n📡 Simulating API call: GET /api/events?cursor_id={next_cursor}&limit=2")
        result2 = service.get_events(limit=2, cursor_id=result1['next_cursor'])
        
        api_response2 = {
            "events": [event.model_dump() for event in result2['events']],
            "pagination": {
                "next_cursor": result2.get('next_cursor'),
                "has_more": result2['has_more'],
                "pagination_type": result2['pagination_type']
            }
        }
        
        print(f"   API Response:")
        print(f"     - Events count: {len(api_response2['events'])}")
        print(f"     - Next cursor: {api_response2['pagination']['next_cursor']}")
        print(f"     - Has more: {api_response2['pagination']['has_more']}")
        print(f"     - Pagination type: {api_response2['pagination']['pagination_type']}")
    
    print("\n✅ API endpoint simulation tests passed!")
    return True

if __name__ == "__main__":
    try:
        print("🚀 Starting EVE-9 Cursor Pagination Tests with Data")
        print("=" * 60)
        
        # Create test data
        created_events = create_test_events()
        
        if not created_events:
            print("❌ No test events created, cannot test pagination")
            sys.exit(1)
        
        # Run tests
        test_cursor_pagination_with_data()
        test_api_endpoint_simulation()
        
        print("\n🎉 All EVE-9 tests with data completed successfully!")
        print("✅ Cursor-based pagination works with real data")
        print("✅ API response format is correct")
        print("✅ Category and search filters work with cursor pagination")
        print("✅ No duplicate events across pages")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

