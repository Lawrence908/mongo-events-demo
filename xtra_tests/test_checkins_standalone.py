#!/usr/bin/env python3
"""
Standalone test for enhanced check-ins functionality.
This test runs without requiring MongoDB connection.
"""

import sys
import os
from datetime import datetime, timezone
from bson import ObjectId
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the database connection before importing
with patch.dict(os.environ, {'MONGODB_URI': 'mongodb://localhost:27017/', 'MONGODB_DB_NAME': 'test_events_demo'}):
    # Mock the database connection
    mock_db = Mock()
    mock_checkins = Mock()
    mock_db.checkins = mock_checkins
    
    with patch('app.database.get_mongodb', return_value=mock_db):
        with patch('app.database.mongodb'):
            from app.models import CheckinCreate, CheckinUpdate, CheckinMetadata, EventLocation, Checkin
            from app.services import CheckinService


def test_checkin_models():
    """Test check-in model validation"""
    print("Testing CheckinCreate model...")
    
    # Test with all fields
    sample_data = {
        "eventId": str(ObjectId()),
        "userId": str(ObjectId()),
        "venueId": str(ObjectId()),
        "qrCode": "QR123456789",
        "ticketTier": "VIP",
        "checkInMethod": "qr_code",
        "location": {
            "type": "Point",
            "coordinates": [-74.0060, 40.7128]
        },
        "metadata": {
            "deviceInfo": "iPhone 13 Pro",
            "ipAddress": "192.168.1.100",
            "staffVerified": True
        }
    }
    
    checkin = CheckinCreate(**sample_data)
    assert checkin.eventId == ObjectId(sample_data["eventId"])
    assert checkin.userId == ObjectId(sample_data["userId"])
    assert checkin.venueId == ObjectId(sample_data["venueId"])
    assert checkin.qrCode == sample_data["qrCode"]
    assert checkin.ticketTier == sample_data["ticketTier"]
    assert checkin.checkInMethod == sample_data["checkInMethod"]
    assert checkin.location.type == "Point"
    assert checkin.metadata.deviceInfo == "iPhone 13 Pro"
    assert checkin.metadata.staffVerified is True
    print("✅ CheckinCreate model validation passed")
    
    # Test with minimal fields
    minimal_data = {
        "event_id": str(ObjectId()),
        "user_id": str(ObjectId()),
        "venue_id": str(ObjectId()),
        "qr_code": "QR123"
    }
    
    minimal_checkin = CheckinCreate(**minimal_data)
    assert minimal_checkin.event_id == ObjectId(minimal_data["event_id"])
    assert minimal_checkin.user_id == ObjectId(minimal_data["user_id"])
    assert minimal_checkin.venue_id == ObjectId(minimal_data["venue_id"])
    assert minimal_checkin.qr_code == minimal_data["qr_code"]
    assert minimal_checkin.ticket_tier is None
    assert minimal_checkin.check_in_method is None
    assert minimal_checkin.location is None
    assert minimal_checkin.metadata is None
    print("✅ Minimal CheckinCreate model validation passed")


def test_checkin_metadata():
    """Test CheckinMetadata model"""
    print("Testing CheckinMetadata model...")
    
    metadata = CheckinMetadata(
        device_info="Android 12",
        ip_address="10.0.0.1",
        staff_verified=False
    )
    assert metadata.device_info == "Android 12"
    assert metadata.ip_address == "10.0.0.1"
    assert metadata.staff_verified is False
    print("✅ CheckinMetadata model validation passed")


def test_checkin_update():
    """Test CheckinUpdate model"""
    print("Testing CheckinUpdate model...")
    
    update_data = {
        "qr_code": "QR987654321",
        "ticket_tier": "General",
        "check_in_method": "manual",
        "metadata": CheckinMetadata(
            device_info="Chrome Browser",
            ip_address="203.0.113.1"
        )
    }
    update = CheckinUpdate(**update_data)
    assert update.qr_code == update_data["qr_code"]
    assert update.ticket_tier == update_data["ticket_tier"]
    assert update.check_in_method == update_data["check_in_method"]
    assert update.metadata.device_info == "Chrome Browser"
    print("✅ CheckinUpdate model validation passed")


def test_coordinate_validation():
    """Test coordinate validation"""
    print("Testing coordinate validation...")
    
    # Valid coordinates
    valid_location = EventLocation(
        type="Point",
        coordinates=[-74.0060, 40.7128]
    )
    assert valid_location.coordinates == [-74.0060, 40.7128]
    print("✅ Valid coordinates passed")
    
    # Test invalid longitude
    try:
        EventLocation(type="Point", coordinates=[200.0, 40.7128])
        assert False, "Should have raised ValueError for invalid longitude"
    except ValueError as e:
        assert "Longitude must be between -180 and 180" in str(e)
        print("✅ Invalid longitude validation passed")
    
    # Test invalid latitude
    try:
        EventLocation(type="Point", coordinates=[-74.0060, 100.0])
        assert False, "Should have raised ValueError for invalid latitude"
    except ValueError as e:
        assert "Latitude must be between -90 and 90" in str(e)
        print("✅ Invalid latitude validation passed")


def test_checkin_service_creation():
    """Test CheckinService creation"""
    print("Testing CheckinService creation...")
    
    service = CheckinService()
    assert service is not None
    assert service.db is None  # Should be None initially
    print("✅ CheckinService creation passed")


def test_checkin_service_with_mocked_db():
    """Test CheckinService with mocked database"""
    print("Testing CheckinService with mocked database...")
    
    service = CheckinService()
    service.db = mock_db
    
    # Test get_checkin with invalid ID
    result = service.get_checkin("invalid_id")
    assert result is None
    print("✅ Invalid ObjectId handling passed")
    
    # Test get_checkins_by_user with invalid ID
    result = service.get_checkins_by_user("invalid_id")
    assert result["checkins"] == []
    assert result["has_more"] is False
    print("✅ Invalid user ID handling passed")


def test_analytics_methods():
    """Test analytics methods with mocked data"""
    print("Testing analytics methods...")
    
    service = CheckinService()
    service.db = mock_db
    
    # Mock aggregation results
    mock_stats = {
        "total_checkins": 25,
        "unique_users": 20,
        "checkin_methods": {"qr_code": 15, "manual": 10},
        "avg_checkin_time": datetime.now(timezone.utc)
    }
    mock_db.checkins.aggregate.return_value = [mock_stats]
    
    # Test attendance stats
    result = service.get_attendance_stats_by_event(str(ObjectId()))
    assert result["total_checkins"] == 25
    assert result["unique_users"] == 20
    assert "qr_code" in result["checkin_methods"]
    print("✅ Analytics methods passed")


def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Enhanced Check-ins Tests...")
    print("=" * 50)
    
    try:
        test_checkin_models()
        test_checkin_metadata()
        test_checkin_update()
        test_coordinate_validation()
        test_checkin_service_creation()
        test_checkin_service_with_mocked_db()
        test_analytics_methods()
        
        print("=" * 50)
        print("🎉 All tests passed successfully!")
        print("✅ Enhanced check-ins implementation is working correctly")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
