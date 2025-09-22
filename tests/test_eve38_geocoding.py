"""
Test suite for EVE-38: Event address support with geocoding

This test suite validates the Google Maps geocoding integration including:
- Address to coordinates conversion
- Coordinates to address conversion (reverse geocoding)
- Directions URL generation
- Error handling for geocoding failures
- Event creation and updates with address support
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from bson import ObjectId

from app.models import EventCreate, EventUpdate, EventAddress, EventLocation
from app.geocoding import GeocodingService, GeocodingError
from app.services import EventService


class TestGeocodingService:
    """Test the GeocodingService class"""
    
    def test_geocoding_service_initialization_without_api_key(self):
        """Test that GeocodingService raises error when no API key is provided"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(GeocodingError, match="Google Maps API key is required"):
                GeocodingService()
    
    def test_geocoding_service_initialization_with_api_key(self):
        """Test that GeocodingService initializes correctly with API key"""
        with patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test-key"}):
            service = GeocodingService()
            assert service.api_key == "test-key"
            assert service.geocoding_url == "https://maps.googleapis.com/maps/api/geocode/json"
    
    @patch('requests.get')
    def test_geocode_address_success(self, mock_get):
        """Test successful address geocoding"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "OK",
            "results": [{
                "geometry": {
                    "location": {
                        "lng": -122.4194,
                        "lat": 37.7749
                    }
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = GeocodingService("test-key")
        address = EventAddress(
            street="123 Main St",
            city="San Francisco",
            state="CA",
            zip="94102",
            country="USA"
        )
        
        lng, lat = service.geocode_address(address)
        assert lng == -122.4194
        assert lat == 37.7749
        
        # Verify API call was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "address" in call_args[1]["params"]
        assert "key" in call_args[1]["params"]
        assert call_args[1]["params"]["key"] == "test-key"
    
    @patch('requests.get')
    def test_geocode_address_api_error(self, mock_get):
        """Test geocoding with API error response"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "ZERO_RESULTS"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = GeocodingService("test-key")
        address = EventAddress(
            street="Invalid Address",
            city="Nowhere",
            state="XX",
            zip="00000",
            country="USA"
        )
        
        with pytest.raises(GeocodingError, match="Geocoding failed: ZERO_RESULTS"):
            service.geocode_address(address)
    
    @patch('requests.get')
    def test_reverse_geocode_success(self, mock_get):
        """Test successful reverse geocoding"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "OK",
            "results": [{
                "address_components": [
                    {"types": ["street_number"], "long_name": "123"},
                    {"types": ["route"], "long_name": "Main St"},
                    {"types": ["locality"], "long_name": "San Francisco"},
                    {"types": ["administrative_area_level_1"], "long_name": "CA"},
                    {"types": ["postal_code"], "long_name": "94102"},
                    {"types": ["country"], "long_name": "USA"}
                ]
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = GeocodingService("test-key")
        address = service.reverse_geocode(-122.4194, 37.7749)
        
        assert address.street == "123 Main St"
        assert address.city == "San Francisco"
        assert address.state == "CA"
        assert address.zip == "94102"
        assert address.country == "USA"
    
    @patch('requests.get')
    def test_reverse_geocode_incomplete_address(self, mock_get):
        """Test reverse geocoding with incomplete address components"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "OK",
            "results": [{
                "address_components": [
                    {"types": ["country"], "long_name": "USA"}
                    # Missing other components
                ]
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = GeocodingService("test-key")
        
        with pytest.raises(GeocodingError, match="Could not parse complete address"):
            service.reverse_geocode(-122.4194, 37.7749)
    
    def test_generate_directions_url_with_address(self):
        """Test directions URL generation with address"""
        service = GeocodingService("test-key")
        url = service.generate_directions_url(destination_address="123 Main St, San Francisco, CA")
        
        assert "https://www.google.com/maps/dir/?api=1" in url
        assert "destination=" in url
    
    def test_generate_directions_url_with_coordinates(self):
        """Test directions URL generation with coordinates"""
        service = GeocodingService("test-key")
        url = service.generate_directions_url(destination_coords=(-122.4194, 37.7749))
        
        assert "https://www.google.com/maps/dir/?api=1" in url
        assert "destination=37.7749,-122.4194" in url
    
    def test_generate_directions_url_no_params(self):
        """Test directions URL generation with no parameters"""
        service = GeocodingService("test-key")
        
        with pytest.raises(GeocodingError, match="Either destination_address or destination_coords must be provided"):
            service.generate_directions_url()
    
    @patch('requests.get')
    def test_validate_and_geocode_event_with_address(self, mock_get):
        """Test event validation with address geocoding"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "OK",
            "results": [{
                "geometry": {
                    "location": {
                        "lng": -122.4194,
                        "lat": 37.7749
                    }
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = GeocodingService("test-key")
        
        event_data = {
            "title": "Test Event",
            "category": "Test",
            "address": {
                "street": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "zip": "94102",
                "country": "USA"
            }
        }
        
        result = service.validate_and_geocode_event(event_data)
        
        assert "location" in result
        assert result["location"]["coordinates"] == [-122.4194, 37.7749]
        assert "directions_url" in result
        assert "address" in result
    
    @patch('requests.get')
    def test_validate_and_geocode_event_with_coordinates(self, mock_get):
        """Test event validation with coordinate reverse geocoding"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "OK",
            "results": [{
                "address_components": [
                    {"types": ["street_number"], "long_name": "123"},
                    {"types": ["route"], "long_name": "Main St"},
                    {"types": ["locality"], "long_name": "San Francisco"},
                    {"types": ["administrative_area_level_1"], "long_name": "CA"},
                    {"types": ["postal_code"], "long_name": "94102"},
                    {"types": ["country"], "long_name": "USA"}
                ]
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = GeocodingService("test-key")
        
        event_data = {
            "title": "Test Event",
            "category": "Test",
            "location": {
                "type": "Point",
                "coordinates": [-122.4194, 37.7749]
            }
        }
        
        result = service.validate_and_geocode_event(event_data)
        
        assert "address" in result
        assert result["address"]["street"] == "123 Main St"
        assert result["address"]["city"] == "San Francisco"
        assert "directions_url" in result
    
    def test_validate_and_geocode_event_no_location_data(self):
        """Test event validation with no location data"""
        service = GeocodingService("test-key")
        
        event_data = {
            "title": "Test Event",
            "category": "Test"
        }
        
        with pytest.raises(GeocodingError, match="Either address or coordinates must be provided"):
            service.validate_and_geocode_event(event_data)


class TestEventServiceGeocoding:
    """Test EventService integration with geocoding"""
    
    @patch('app.services.get_geocoding_service')
    def test_create_event_with_geocoding_success(self, mock_get_service):
        """Test event creation with successful geocoding"""
        # Mock geocoding service
        mock_service = Mock()
        test_start_date = datetime.now()
        mock_service.validate_and_geocode_event.return_value = {
            "title": "Test Event",
            "category": "Test",
            "start_date": test_start_date,
            "location": {
                "type": "Point",
                "coordinates": [-122.4194, 37.7749]
            },
            "address": {
                "street": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "zip": "94102",
                "country": "USA"
            },
            "directions_url": "https://www.google.com/maps/dir/?api=1&destination=37.7749,-122.4194"
        }
        mock_get_service.return_value = mock_service
        
        # Mock database
        with patch('app.services.get_mongodb') as mock_get_db:
            mock_db = Mock()
            mock_collection = Mock()
            test_object_id = ObjectId()
            mock_collection.insert_one.return_value.inserted_id = test_object_id
            mock_db.events = mock_collection
            mock_get_db.return_value = mock_db
            
            service = EventService()
            event_data = EventCreate(
                title="Test Event",
                category="Test",
                location=EventLocation(coordinates=[-122.4194, 37.7749]),
                start_date=datetime.now()
            )
            
            result = service.create_event(event_data)
            
            # Verify geocoding was called
            mock_service.validate_and_geocode_event.assert_called_once()
            
            # Verify database insert was called
            mock_collection.insert_one.assert_called_once()
    
    @patch('app.services.get_geocoding_service')
    def test_create_event_with_geocoding_failure(self, mock_get_service):
        """Test event creation with geocoding failure (should still create event)"""
        # Mock geocoding service to raise error
        mock_service = Mock()
        mock_service.validate_and_geocode_event.side_effect = GeocodingError("API error")
        mock_get_service.return_value = mock_service
        
        # Mock database
        with patch('app.services.get_mongodb') as mock_get_db:
            mock_db = Mock()
            mock_collection = Mock()
            test_object_id = ObjectId()
            mock_collection.insert_one.return_value.inserted_id = test_object_id
            mock_db.events = mock_collection
            mock_get_db.return_value = mock_db
            
            service = EventService()
            event_data = EventCreate(
                title="Test Event",
                category="Test",
                location=EventLocation(coordinates=[-122.4194, 37.7749]),
                start_date=datetime.now()
            )
            
            # Should not raise error, just log warning
            result = service.create_event(event_data)
            
            # Verify database insert was still called
            mock_collection.insert_one.assert_called_once()
    
    @patch('app.services.get_geocoding_service')
    def test_update_event_with_geocoding(self, mock_get_service):
        """Test event update with geocoding"""
        # Mock geocoding service
        mock_service = Mock()
        mock_service.validate_and_geocode_event.return_value = {
            "title": "Updated Event",
            "category": "Test",
            "location": {
                "type": "Point",
                "coordinates": [-122.4194, 37.7749]
            },
            "address": {
                "street": "456 New St",
                "city": "San Francisco",
                "state": "CA",
                "zip": "94103",
                "country": "USA"
            },
            "directions_url": "https://www.google.com/maps/dir/?api=1&destination=37.7749,-122.4194"
        }
        mock_get_service.return_value = mock_service
        
        # Mock database and existing event
        with patch('app.services.get_mongodb') as mock_get_db:
            mock_db = Mock()
            mock_collection = Mock()
            test_object_id = ObjectId()
            mock_collection.update_one.return_value.matched_count = 1
            mock_collection.find_one.return_value = {
                "_id": test_object_id,
                "title": "Test Event",
                "category": "Test",
                "location": {"type": "Point", "coordinates": [-122.4194, 37.7749]},
                "start_date": datetime.now()
            }
            mock_db.events = mock_collection
            mock_get_db.return_value = mock_db
            
            service = EventService()
            event_data = EventUpdate(
                address=EventAddress(
                    street="456 New St",
                    city="San Francisco",
                    state="CA",
                    zip="94103",
                    country="USA"
                )
            )
            
            result = service.update_event(str(test_object_id), event_data)
            
            # Verify geocoding was called
            mock_service.validate_and_geocode_event.assert_called_once()
            
            # Verify database update was called
            mock_collection.update_one.assert_called_once()


class TestGeocodingIntegration:
    """Integration tests for geocoding functionality"""
    
    def test_event_model_with_address_fields(self):
        """Test that Event models support address and directions_url fields"""
        # Test EventCreate with address
        event_create = EventCreate(
            title="Test Event",
            category="Test",
            location=EventLocation(coordinates=[-122.4194, 37.7749]),
            address=EventAddress(
                street="123 Main St",
                city="San Francisco",
                state="CA",
                zip="94102",
                country="USA"
            ),
            directions_url="https://www.google.com/maps/dir/?api=1&destination=37.7749,-122.4194",
            start_date=datetime.now()
        )
        
        assert event_create.address is not None
        assert event_create.address.street == "123 Main St"
        assert event_create.directions_url is not None
        
        # Test EventUpdate with address
        event_update = EventUpdate(
            address=EventAddress(
                street="456 New St",
                city="San Francisco",
                state="CA",
                zip="94103",
                country="USA"
            ),
            directions_url="https://www.google.com/maps/dir/?api=1&destination=37.7749,-122.4194"
        )
        
        assert event_update.address is not None
        assert event_update.directions_url is not None
    
    def test_event_address_validation(self):
        """Test EventAddress model validation"""
        # Valid address
        address = EventAddress(
            street="123 Main St",
            city="San Francisco",
            state="CA",
            zip="94102",
            country="USA"
        )
        assert address.street == "123 Main St"
        assert address.city == "San Francisco"
        
        # Test validation errors
        with pytest.raises(ValueError):
            EventAddress(
                street="",  # Empty street should fail
                city="San Francisco",
                state="CA",
                zip="94102",
                country="USA"
            )


if __name__ == "__main__":
    pytest.main([__file__])
