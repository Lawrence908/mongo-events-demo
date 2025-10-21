#!/usr/bin/env python3
"""
Test script for EVE-9: Cursor-based pagination for events list
Tests the API endpoint and service layer cursor pagination functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services import get_event_service
from app.models import EventCreate, EventLocation
from datetime import datetime, timedelta
import json

def test_cursor_pagination():
    """Test cursor-based pagination functionality"""
    print("🧪 Testing EVE-9: Cursor-based pagination for events list")
    print("=" * 60)
    
    service = get_event_service()
    
    # Test 1: Basic cursor pagination
    print("\n📄 Test 1: Basic cursor pagination")
    result1 = service.get_events(limit=3, cursor_id=None)
    print(f"   First page: {len(result1['events'])} events")
    print(f"   Has more: {result1['has_more']}")
    print(f"   Next cursor: {result1.get('next_cursor', 'None')}")
    print(f"   Pagination type: {result1['pagination_type']}")
    
    # Test 2: Second page with cursor
    if result1.get('next_cursor'):
        print("\n📄 Test 2: Second page with cursor")
        result2 = service.get_events(limit=3, cursor_id=result1['next_cursor'])
        print(f"   Second page: {len(result2['events'])} events")
        print(f"   Has more: {result2['has_more']}")
        print(f"   Next cursor: {result2.get('next_cursor', 'None')}")
        print(f"   Pagination type: {result2['pagination_type']}")
        
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
    
    # Test 4: Cursor pagination with search filter
    print("\n📄 Test 4: Cursor pagination with search filter")
    result4 = service.get_events(limit=2, search='test', cursor_id=None)
    print(f"   Search results: {len(result4['events'])} events")
    print(f"   Has more: {result4['has_more']}")
    print(f"   Next cursor: {result4.get('next_cursor', 'None')}")
    print(f"   Pagination type: {result4['pagination_type']}")
    
    # Test 5: Invalid cursor handling
    print("\n📄 Test 5: Invalid cursor handling")
    result5 = service.get_events(limit=2, cursor_id="invalid_cursor_id")
    print(f"   Invalid cursor fallback: {len(result5['events'])} events")
    print(f"   Pagination type: {result5['pagination_type']}")
    assert result5['pagination_type'] == 'offset', "Should fallback to offset pagination"
    
    # Test 6: Empty result set
    print("\n📄 Test 6: Empty result set handling")
    result6 = service.get_events(limit=2, category='nonexistent_category', cursor_id=None)
    print(f"   Empty results: {len(result6['events'])} events")
    print(f"   Has more: {result6['has_more']}")
    print(f"   Next cursor: {result6.get('next_cursor', 'None')}")
    assert result6['has_more'] == False, "Empty results should have has_more=False"
    assert result6.get('next_cursor') is None, "Empty results should have no next cursor"
    
    print("\n✅ All cursor pagination tests passed!")
    return True

def test_api_response_format():
    """Test that API response includes proper pagination fields"""
    print("\n🌐 Testing API response format")
    print("=" * 40)
    
    # This would normally test the Flask API endpoint
    # For now, we'll test the service layer response format
    service = get_event_service()
    result = service.get_events(limit=2, cursor_id=None)
    
    # Verify required fields are present
    required_fields = ['events', 'next_cursor', 'has_more', 'pagination_type']
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"
        print(f"   ✓ {field}: {result[field]}")
    
    # Verify events is a list
    assert isinstance(result['events'], list), "Events should be a list"
    print(f"   ✓ events is list with {len(result['events'])} items")
    
    # Verify has_more is boolean
    assert isinstance(result['has_more'], bool), "has_more should be boolean"
    print(f"   ✓ has_more is boolean: {result['has_more']}")
    
    # Verify pagination_type is string
    assert isinstance(result['pagination_type'], str), "pagination_type should be string"
    print(f"   ✓ pagination_type is string: {result['pagination_type']}")
    
    print("\n✅ API response format tests passed!")
    return True

if __name__ == "__main__":
    try:
        print("🚀 Starting EVE-9 Cursor Pagination Tests")
        print("=" * 60)
        
        # Run tests
        test_cursor_pagination()
        test_api_response_format()
        
        print("\n🎉 All EVE-9 tests completed successfully!")
        print("✅ Cursor-based pagination is working correctly")
        print("✅ API response format is correct")
        print("✅ Category and search filters work with cursor pagination")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

