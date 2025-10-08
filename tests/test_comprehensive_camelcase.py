#!/usr/bin/env python3
"""
Comprehensive test suite for MongoDB Events Demo with camelCase field names.
This test consolidates the most important functionality tests.
"""

import os
import sys
from datetime import datetime, timezone
from bson import ObjectId
import pytest

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import get_mongodb
from app.models import (
    EventCreate, EventLocation, EventUpdate,
    VenueCreate, VenueUpdate, VenueAddress, VenueContact,
    UserCreate, UserUpdate, UserProfile, UserPreferences,
    CheckinCreate, CheckinUpdate, CheckinMetadata
)


@pytest.fixture
def app():
    """Create test app"""
    os.environ["MONGODB_DB_NAME"] = "test_events_demo"
    app_tup = create_app()
    app = app_tup[0] if isinstance(app_tup, tuple) else app_tup
    app.config["TESTING"] = True
    yield app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def db():
    """Create test database connection"""
    os.environ["MONGODB_DB_NAME"] = "test_events_demo"
    mongodb = get_mongodb()
    yield mongodb
    # Clean up test data after each test
    mongodb.events.delete_many({})
    mongodb.venues.delete_many({})
    mongodb.users.delete_many({})
    mongodb.checkins.delete_many({})


class TestModels:
    """Test Pydantic models with camelCase fields"""

    def test_event_location_valid(self):
        """Test valid event location"""
        location = EventLocation(coordinates=[-74.0060, 40.7128])
        assert location.type == "Point"
        assert location.coordinates == [-74.0060, 40.7128]

    def test_event_create_valid(self):
        """Test valid event creation with camelCase fields"""
        event_data = {
            "title": "Test Event",
            "category": "conference",
            "eventType": "inPerson",
            "location": {"coordinates": [-74.0060, 40.7128]},
            "startDate": datetime.now(),
        }

        event = EventCreate(**event_data)
        assert event.title == "Test Event"
        assert event.category == "conference"
        assert event.eventType == "inPerson"
        assert event.location.coordinates == [-74.0060, 40.7128]

    def test_venue_create_valid(self):
        """Test valid venue creation with camelCase fields"""
        venue_data = {
            "name": "Test Venue",
            "venueType": "conferenceCenter",
            "location": {"coordinates": [-74.0060, 40.7128]},
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            "capacity": 100
        }

        venue = VenueCreate(**venue_data)
        assert venue.name == "Test Venue"
        assert venue.venueType == "conferenceCenter"
        assert venue.capacity == 100

    def test_user_create_valid(self):
        """Test valid user creation with camelCase fields"""
        user_data = {
            "email": "test@example.com",
            "profile": {
                "firstName": "John",
                "lastName": "Doe",
                "preferences": {
                    "radiusKm": 10.0
                }
            }
        }

        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        assert user.profile.firstName == "John"
        assert user.profile.lastName == "Doe"
        assert user.profile.preferences.radiusKm == 10.0

    def test_checkin_create_valid(self):
        """Test valid check-in creation with camelCase fields"""
        checkin_data = {
            "eventId": ObjectId(),
            "userId": ObjectId(),
            "venueId": ObjectId(),
            "qrCode": "QR123456",
            "ticketTier": "VIP",
            "checkInMethod": "qrCode",
            "metadata": {
                "deviceInfo": "iPhone 13",
                "ipAddress": "192.168.1.1",
                "staffVerified": True
            }
        }

        checkin = CheckinCreate(**checkin_data)
        assert checkin.eventId == checkin_data["eventId"]
        assert checkin.userId == checkin_data["userId"]
        assert checkin.venueId == checkin_data["venueId"]
        assert checkin.qrCode == "QR123456"
        assert checkin.ticketTier == "VIP"
        assert checkin.checkInMethod == "qrCode"


class TestAPI:
    """Test API endpoints with camelCase field names"""

    def test_index_page(self, client):
        """Test index page loads"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Events Map" in response.data

    def test_events_list_page(self, client):
        """Test events list page loads"""
        response = client.get("/events")
        assert response.status_code == 200
        assert b"Events" in response.data

    def test_create_event_page(self, client):
        """Test create event page loads"""
        response = client.get("/events/new")
        assert response.status_code == 200
        assert b"Create New Event" in response.data

    def test_api_get_events_empty(self, client, db):
        """Test API returns empty events list"""
        response = client.get("/api/events")
        assert response.status_code == 200

        data = response.get_json()
        assert "events" in data
        assert len(data["events"]) == 0

    def test_api_nearby_events(self, client):
        """Test nearby events API"""
        response = client.get("/api/events/nearby?lat=40.7128&lng=-74.0060&radius=10")
        assert response.status_code == 200

        data = response.get_json()
        assert "type" in data
        assert data["type"] == "FeatureCollection"
        assert "features" in data

    def test_api_create_event(self, client, db):
        """Test creating event via API with camelCase fields"""
        event_data = {
            "title": "API Test Event",
            "category": "test",
            "eventType": "inPerson",
            "location": {"coordinates": [-74.0060, 40.7128]},
            "startDate": "2024-12-01T10:00:00",
        }

        response = client.post(
            "/api/events", json=event_data, content_type="application/json"
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["title"] == "API Test Event"
        assert "id" in data


class TestDatabaseOperations:
    """Test database operations with camelCase field names"""

    def test_database_connection(self, db):
        """Test database connection"""
        assert db.is_connected()

    def test_create_and_retrieve_event(self, db):
        """Test creating and retrieving events with camelCase fields"""
        from app.services import get_event_service

        event_data = EventCreate(
            title="Test DB Event",
            category="conference",
            eventType="inPerson",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            startDate=datetime.now(),
        )

        event_service = get_event_service()
        created_event = event_service.create_event(event_data)
        assert created_event.id is not None
        assert created_event.title == "Test DB Event"

        # Test retrieval
        retrieved_event = event_service.get_event(str(created_event.id))
        assert retrieved_event is not None
        assert retrieved_event.title == "Test DB Event"

    def test_create_and_retrieve_venue(self, db):
        """Test creating and retrieving venues with camelCase fields"""
        from app.services import get_venue_service

        venue_data = VenueCreate(
            name="Test Venue",
            venueType="conferenceCenter",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            address=VenueAddress(
                street="123 Main St",
                city="New York",
                state="NY",
                zip="10001",
                country="USA"
            ),
            capacity=100
        )

        venue_service = get_venue_service()
        created_venue = venue_service.create_venue(venue_data)
        assert created_venue.id is not None
        assert created_venue.name == "Test Venue"
        assert created_venue.venueType == "conferenceCenter"

    def test_create_and_retrieve_user(self, db):
        """Test creating and retrieving users with camelCase fields"""
        from app.services import get_user_service

        user_data = UserCreate(
            email="test@example.com",
            profile=UserProfile(
                firstName="John",
                lastName="Doe",
                preferences=UserPreferences(
                    radiusKm=10.0
                )
            )
        )

        user_service = get_user_service()
        created_user = user_service.create_user(user_data)
        assert created_user.id is not None
        assert created_user.email == "test@example.com"
        assert created_user.profile.firstName == "John"
        assert created_user.profile.lastName == "Doe"

    def test_create_and_retrieve_checkin(self, db):
        """Test creating and retrieving check-ins with camelCase fields"""
        from app.services import get_event_service, get_user_service, get_checkin_service

        # Create event and user first
        event_service = get_event_service()
        user_service = get_user_service()
        checkin_service = get_checkin_service()

        event_data = EventCreate(
            title="Test Event",
            category="conference",
            eventType="inPerson",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            startDate=datetime.now(),
        )
        created_event = event_service.create_event(event_data)

        user_data = UserCreate(
            email="test@example.com",
            profile=UserProfile(
                firstName="John",
                lastName="Doe"
            )
        )
        created_user = user_service.create_user(user_data)

        # Create check-in
        checkin_data = CheckinCreate(
            eventId=created_event.id,
            userId=created_user.id,
            venueId=ObjectId(),  # Mock venue ID
            qrCode="QR123456",
            ticketTier="VIP",
            metadata=CheckinMetadata(
                deviceInfo="iPhone 13",
                ipAddress="192.168.1.1",
                staffVerified=True
            )
        )

        created_checkin = checkin_service.create_checkin(checkin_data)
        assert created_checkin.id is not None
        assert created_checkin.eventId == created_event.id
        assert created_checkin.userId == created_user.id
        assert created_checkin.qrCode == "QR123456"
        assert created_checkin.ticketTier == "VIP"


class TestGeospatialQueries:
    """Test geospatial queries with camelCase field names"""

    def test_nearby_events_search(self, db):
        """Test nearby events search"""
        from app.services import get_event_service
        from app.models import EventsNearbyQuery

        # Create a test event
        event_data = EventCreate(
            title="NYC Event",
            category="conference",
            eventType="inPerson",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),  # NYC
            startDate=datetime.now(),
        )

        event_service = get_event_service()
        event_service.create_event(event_data)

        # Test nearby search
        query = EventsNearbyQuery(longitude=-74.0060, latitude=40.7128, radiusKm=1)
        result = event_service.get_events_nearby(query)

        assert result is not None
        assert len(result) >= 1


class TestTextSearch:
    """Test text search functionality"""

    def test_text_search_events(self, db):
        """Test text search for events"""
        from app.services import get_event_service

        # Create events with searchable content
        events_data = [
            EventCreate(
                title="Python Conference 2024",
                category="Technology",
                eventType="inPerson",
                location=EventLocation(coordinates=[-74.0060, 40.7128]),
                startDate=datetime.now(),
                description="Learn Python programming"
            ),
            EventCreate(
                title="JavaScript Workshop",
                category="Technology", 
                eventType="virtual",
                location=EventLocation(coordinates=[-74.0060, 40.7128]),
                startDate=datetime.now(),
                description="Modern JavaScript development"
            )
        ]

        event_service = get_event_service()
        for event_data in events_data:
            event_service.create_event(event_data)

        # Test text search
        results = event_service.search_events("Python")
        assert len(results) >= 1
        assert any("Python" in event.title for event in results)


class TestPerformance:
    """Test performance with camelCase field names"""

    def test_large_dataset_performance(self, db):
        """Test performance with larger dataset"""
        from app.services import get_event_service
        import time

        event_service = get_event_service()
        
        # Create multiple events
        start_time = time.time()
        for i in range(50):
            event_data = EventCreate(
                title=f"Test Event {i}",
                category="Technology",
                eventType="inPerson",
                location=EventLocation(coordinates=[-74.0060 + i*0.001, 40.7128 + i*0.001]),
                startDate=datetime.now(),
            )
            event_service.create_event(event_data)
        
        creation_time = time.time() - start_time
        print(f"Created 50 events in {creation_time:.2f} seconds")
        
        # Test retrieval performance
        start_time = time.time()
        events = event_service.get_events()
        retrieval_time = time.time() - start_time
        print(f"Retrieved {len(events)} events in {retrieval_time:.2f} seconds")
        
        assert len(events) >= 50
        assert retrieval_time < 1.0  # Should be fast


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
