"""
Unit tests for enhanced check-ins bridge table functionality.
Tests cover CRUD operations, duplicate prevention, analytics queries, and schema validation.
"""

import pytest
import os
import sys
from datetime import datetime, timezone
from bson import ObjectId
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock MongoDB connection before importing app modules
with patch.dict(os.environ, {'MONGODB_URI': 'mongodb://localhost:27017/', 'MONGODB_DB_NAME': 'test_events_demo'}):
    from app.models import CheckinCreate, CheckinUpdate, CheckinMetadata, EventLocation, Checkin
    from app.services import CheckinService


class TestEnhancedCheckins:
    """Test suite for enhanced check-ins bridge table functionality"""

    @pytest.fixture
    def checkin_service(self):
        """Create a CheckinService instance for testing"""
        return CheckinService()

    @pytest.fixture
    def sample_checkin_data(self):
        """Sample check-in data for testing"""
        return {
            "event_id": str(ObjectId()),
            "user_id": str(ObjectId()),
            "venue_id": str(ObjectId()),
            "qr_code": "QR123456789",
            "ticket_tier": "VIP",
            "check_in_method": "qr_code",
            "location": {
                "type": "Point",
                "coordinates": [-74.0060, 40.7128]
            },
            "metadata": {
                "device_info": "iPhone 13 Pro",
                "ip_address": "192.168.1.100",
                "staff_verified": True
            }
        }

    @pytest.fixture
    def mock_db(self):
        """Mock database for testing"""
        mock_db = Mock()
        mock_checkins = Mock()
        mock_db.checkins = mock_checkins
        return mock_db

    def test_checkin_create_model_validation(self, sample_checkin_data):
        """Test CheckinCreate model validation with enhanced fields"""
        # Test valid data
        checkin = CheckinCreate(**sample_checkin_data)
        assert checkin.event_id == ObjectId(sample_checkin_data["event_id"])
        assert checkin.user_id == ObjectId(sample_checkin_data["user_id"])
        assert checkin.venue_id == ObjectId(sample_checkin_data["venue_id"])
        assert checkin.qr_code == sample_checkin_data["qr_code"]
        assert checkin.ticket_tier == sample_checkin_data["ticket_tier"]
        assert checkin.check_in_method == sample_checkin_data["check_in_method"]
        assert checkin.location.type == "Point"
        assert checkin.metadata.device_info == "iPhone 13 Pro"
        assert checkin.metadata.staff_verified is True

    def test_checkin_metadata_validation(self):
        """Test CheckinMetadata model validation"""
        metadata = CheckinMetadata(
            device_info="Android 12",
            ip_address="10.0.0.1",
            staff_verified=False
        )
        assert metadata.device_info == "Android 12"
        assert metadata.ip_address == "10.0.0.1"
        assert metadata.staff_verified is False

    def test_checkin_create_with_minimal_data(self):
        """Test CheckinCreate with minimal required fields"""
        minimal_data = {
            "event_id": str(ObjectId()),
            "user_id": str(ObjectId()),
            "venue_id": str(ObjectId()),
            "qr_code": "QR123"
        }
        checkin = CheckinCreate(**minimal_data)
        assert checkin.event_id == ObjectId(minimal_data["event_id"])
        assert checkin.user_id == ObjectId(minimal_data["user_id"])
        assert checkin.venue_id == ObjectId(minimal_data["venue_id"])
        assert checkin.qr_code == minimal_data["qr_code"]
        assert checkin.ticket_tier is None
        assert checkin.check_in_method is None
        assert checkin.location is None
        assert checkin.metadata is None

    def test_checkin_update_model(self):
        """Test CheckinUpdate model with optional fields"""
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

    @patch('app.services.get_mongodb')
    @patch('app.database.mongodb')
    def test_create_checkin_with_duplicate_prevention(self, mock_mongodb, mock_get_mongodb, checkin_service, sample_checkin_data, mock_db):
        """Test create_checkin with duplicate prevention"""
        mock_get_mongodb.return_value = mock_db
        
        # Mock existing check-in found
        mock_db.checkins.find_one.return_value = {"_id": ObjectId(), "event_id": ObjectId(sample_checkin_data["event_id"])}
        
        checkin_data = CheckinCreate(**sample_checkin_data)
        
        with pytest.raises(ValueError, match="User has already checked in to this event"):
            checkin_service.create_checkin(checkin_data)

    @patch('app.services.get_mongodb')
    def test_create_checkin_success(self, mock_get_mongodb, checkin_service, sample_checkin_data, mock_db):
        """Test successful check-in creation"""
        mock_get_mongodb.return_value = mock_db
        
        # Mock no existing check-in
        mock_db.checkins.find_one.return_value = None
        mock_db.checkins.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        checkin_data = CheckinCreate(**sample_checkin_data)
        result = checkin_service.create_checkin(checkin_data)
        
        assert result is not None
        mock_db.checkins.insert_one.assert_called_once()
        mock_db.checkins.find_one.assert_called_once()

    @patch('app.services.get_mongodb')
    def test_get_checkin_by_event_user(self, mock_get_mongodb, checkin_service, mock_db):
        """Test get_checkin_by_event_user method"""
        mock_get_mongodb.return_value = mock_db
        
        event_id = str(ObjectId())
        user_id = str(ObjectId())
        mock_checkin = {
            "_id": ObjectId(), 
            "event_id": ObjectId(event_id), 
            "user_id": ObjectId(user_id),
            "venue_id": ObjectId(),
            "qr_code": "QR123",
            "check_in_time": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        }
        mock_db.checkins.find_one.return_value = mock_checkin
        
        result = checkin_service.get_checkin_by_event_user(event_id, user_id)
        
        assert result is not None
        mock_db.checkins.find_one.assert_called_once_with({
            "event_id": ObjectId(event_id),
            "user_id": ObjectId(user_id)
        })

    @patch('app.services.get_mongodb')
    def test_get_checkins_by_venue(self, mock_get_mongodb, checkin_service, mock_db):
        """Test get_checkins_by_venue method for analytics"""
        mock_get_mongodb.return_value = mock_db
        
        venue_id = str(ObjectId())
        mock_checkins = [
            {
                "_id": ObjectId(), 
                "venue_id": ObjectId(venue_id), 
                "check_in_time": datetime.now(timezone.utc),
                "event_id": ObjectId(),
                "user_id": ObjectId(),
                "qr_code": "QR123",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "_id": ObjectId(), 
                "venue_id": ObjectId(venue_id), 
                "check_in_time": datetime.now(timezone.utc),
                "event_id": ObjectId(),
                "user_id": ObjectId(),
                "qr_code": "QR456",
                "created_at": datetime.now(timezone.utc)
            }
        ]
        mock_cursor = Mock()
        mock_cursor.__iter__ = Mock(return_value=iter(mock_checkins))
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        mock_db.checkins.find.return_value = mock_cursor
        
        result = checkin_service.get_checkins_by_venue(venue_id, skip=0, limit=10)
        
        assert "checkins" in result
        assert "has_more" in result
        assert "offset" in result
        assert len(result["checkins"]) == 2

    @patch('app.services.get_mongodb')
    def test_get_attendance_stats_by_event(self, mock_get_mongodb, checkin_service, mock_db):
        """Test get_attendance_stats_by_event analytics method"""
        mock_get_mongodb.return_value = mock_db
        
        event_id = str(ObjectId())
        mock_stats = {
            "total_checkins": 25,
            "unique_users": 20,
            "checkin_methods": {"qr_code": 15, "manual": 10},
            "avg_checkin_time": datetime.now(timezone.utc)
        }
        mock_db.checkins.aggregate.return_value = [mock_stats]
        
        result = checkin_service.get_attendance_stats_by_event(event_id)
        
        assert result["total_checkins"] == 25
        assert result["unique_users"] == 20
        assert "qr_code" in result["checkin_methods"]
        assert result["checkin_methods"]["qr_code"] == 15

    @patch('app.services.get_mongodb')
    def test_get_venue_attendance_stats(self, mock_get_mongodb, checkin_service, mock_db):
        """Test get_venue_attendance_stats analytics method"""
        mock_get_mongodb.return_value = mock_db
        
        venue_id = str(ObjectId())
        mock_stats = {
            "total_checkins": 100,
            "unique_users": 75,
            "events_attended": 10,
            "monthly_breakdown": {"2024-01": 30, "2024-02": 35, "2024-03": 35}
        }
        mock_db.checkins.aggregate.return_value = [mock_stats]
        
        result = checkin_service.get_venue_attendance_stats(venue_id)
        
        assert result["total_checkins"] == 100
        assert result["unique_users"] == 75
        assert result["events_attended"] == 10
        assert "2024-01" in result["monthly_breakdown"]

    @patch('app.services.get_mongodb')
    def test_get_repeat_attendees(self, mock_get_mongodb, checkin_service, mock_db):
        """Test get_repeat_attendees analytics method"""
        mock_get_mongodb.return_value = mock_db
        
        mock_repeat_attendees = [
            {
                "user_id": ObjectId(),
                "event_count": 5,
                "events_attended": 5,
                "venues_visited": 3,
                "first_checkin": datetime.now(timezone.utc),
                "last_checkin": datetime.now(timezone.utc)
            },
            {
                "user_id": ObjectId(),
                "event_count": 3,
                "events_attended": 3,
                "venues_visited": 2,
                "first_checkin": datetime.now(timezone.utc),
                "last_checkin": datetime.now(timezone.utc)
            }
        ]
        mock_db.checkins.aggregate.return_value = mock_repeat_attendees
        
        result = checkin_service.get_repeat_attendees(min_events=2)
        
        assert len(result) == 2
        assert result[0]["event_count"] == 5
        assert result[1]["event_count"] == 3

    @patch('app.services.get_mongodb')
    def test_get_checkin_time_patterns(self, mock_get_mongodb, checkin_service, mock_db):
        """Test get_checkin_time_patterns analytics method"""
        mock_get_mongodb.return_value = mock_db
        
        mock_patterns = [
            {"hour": 18, "day_of_week": 5, "checkin_count": 25},
            {"hour": 19, "day_of_week": 5, "checkin_count": 20},
            {"hour": 20, "day_of_week": 6, "checkin_count": 15}
        ]
        mock_db.checkins.aggregate.return_value = mock_patterns
        
        result = checkin_service.get_checkin_time_patterns()
        
        assert "peak_hours" in result
        assert "total_patterns" in result
        assert len(result["peak_hours"]) == 3
        assert result["total_patterns"] == 3

    @patch('app.services.get_mongodb')
    def test_get_user_attendance_history(self, mock_get_mongodb, checkin_service, mock_db):
        """Test get_user_attendance_history analytics method"""
        mock_get_mongodb.return_value = mock_db
        
        user_id = str(ObjectId())
        mock_checkins = [
            {
                "_id": ObjectId(),
                "event_id": ObjectId(),
                "venue_id": ObjectId(),
                "check_in_time": datetime.now(timezone.utc),
                "check_in_method": "qr_code",
                "ticket_tier": "VIP",
                "event_title": "Tech Conference 2024",
                "event_category": "Technology",
                "venue_name": "Convention Center",
                "venue_city": "San Francisco"
            }
        ]
        mock_summary = {
            "total_events": 5,
            "unique_venues": 3,
            "categories_attended": 2,
            "first_checkin": datetime.now(timezone.utc),
            "last_checkin": datetime.now(timezone.utc)
        }
        
        # Mock the aggregation pipeline calls
        mock_db.checkins.aggregate.side_effect = [mock_checkins, [mock_summary]]
        
        result = checkin_service.get_user_attendance_history(user_id)
        
        assert "checkins" in result
        assert "summary" in result
        assert len(result["checkins"]) == 1
        assert result["summary"]["total_events"] == 5

    def test_invalid_objectid_handling(self, checkin_service):
        """Test handling of invalid ObjectId strings"""
        # Test with invalid event_id
        result = checkin_service.get_checkin("invalid_id")
        assert result is None
        
        # Test with invalid user_id
        result = checkin_service.get_checkins_by_user("invalid_id")
        assert result["checkins"] == []
        assert result["has_more"] is False

    def test_checkin_update_with_partial_data(self, checkin_service):
        """Test checkin update with partial data"""
        update_data = CheckinUpdate(
            qr_code="NEW_QR_CODE",
            check_in_method="mobile_app"
        )
        
        # Test that only provided fields are included in update
        update_dict = {
            k: v
            for k, v in update_data.model_dump(exclude_unset=True).items()
            if v is not None
        }
        
        assert "qr_code" in update_dict
        assert "check_in_method" in update_dict
        assert "ticket_tier" not in update_dict
        assert "location" not in update_dict

    def test_coordinate_validation(self):
        """Test coordinate validation in EventLocation"""
        # Valid coordinates
        valid_location = EventLocation(
            type="Point",
            coordinates=[-74.0060, 40.7128]
        )
        assert valid_location.coordinates == [-74.0060, 40.7128]
        
        # Invalid longitude
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            EventLocation(type="Point", coordinates=[200.0, 40.7128])
        
        # Invalid latitude
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            EventLocation(type="Point", coordinates=[-74.0060, 100.0])
        
        # Wrong number of coordinates
        with pytest.raises(ValueError, match="Coordinates must be \\[longitude, latitude\\]"):
            EventLocation(type="Point", coordinates=[-74.0060])

    def test_metadata_validation(self):
        """Test CheckinMetadata validation"""
        # Valid metadata
        metadata = CheckinMetadata(
            device_info="iPhone 13 Pro",
            ip_address="192.168.1.100",
            staff_verified=True
        )
        assert metadata.device_info == "iPhone 13 Pro"
        assert metadata.ip_address == "192.168.1.100"
        assert metadata.staff_verified is True
        
        # Test with None values
        metadata_none = CheckinMetadata()
        assert metadata_none.device_info is None
        assert metadata_none.ip_address is None
        assert metadata_none.staff_verified is None

    def test_checkin_model_with_all_fields(self, sample_checkin_data):
        """Test complete Checkin model with all fields"""
        checkin = CheckinCreate(**sample_checkin_data)
        full_checkin = Checkin(
            **checkin.model_dump(),
            id=ObjectId(),
            check_in_time=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        assert full_checkin.id is not None
        assert full_checkin.check_in_time is not None
        assert full_checkin.created_at is not None
        assert full_checkin.event_id == ObjectId(sample_checkin_data["event_id"])
        assert full_checkin.venue_id == ObjectId(sample_checkin_data["venue_id"])


if __name__ == "__main__":
    pytest.main([__file__])
