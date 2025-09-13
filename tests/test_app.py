import os
import sys
from datetime import datetime

import pytest

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import get_mongodb
from app.models import EventCreate, EventLocation


@pytest.fixture
def app():
    """Create test app"""
    os.environ["MONGODB_DB_NAME"] = "test_events_demo"
    app = create_app()
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


class TestModels:
    """Test Pydantic models"""

    def test_event_location_valid(self):
        """Test valid event location"""
        location = EventLocation(coordinates=[-74.0060, 40.7128])
        assert location.type == "Point"
        assert location.coordinates == [-74.0060, 40.7128]

    def test_event_location_invalid_coordinates(self):
        """Test invalid coordinates"""
        with pytest.raises(ValueError):
            EventLocation(coordinates=[-200, 40.7128])  # Invalid longitude

        with pytest.raises(ValueError):
            EventLocation(coordinates=[-74.0060, 100])  # Invalid latitude

        with pytest.raises(ValueError):
            EventLocation(coordinates=[-74.0060])  # Missing coordinate

    def test_event_create_valid(self):
        """Test valid event creation"""
        event_data = {
            "title": "Test Event",
            "category": "conference",
            "location": {"coordinates": [-74.0060, 40.7128]},
            "start_date": datetime.now(),
        }

        event = EventCreate(**event_data)
        assert event.title == "Test Event"
        assert event.category == "conference"
        assert event.location.coordinates == [-74.0060, 40.7128]


class TestAPI:
    """Test API endpoints"""

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
        """Test creating event via API"""
        event_data = {
            "title": "API Test Event",
            "category": "test",
            "location": {"coordinates": [-74.0060, 40.7128]},
            "start_date": "2024-12-01T10:00:00",
        }

        response = client.post(
            "/api/events", json=event_data, content_type="application/json"
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["title"] == "API Test Event"
        assert "id" in data

    def test_api_create_event_invalid(self, client):
        """Test creating invalid event via API"""
        event_data = {
            "title": "",  # Invalid empty title
            "category": "test",
            "location": {"coordinates": [-74.0060, 40.7128]},
        }

        response = client.post(
            "/api/events", json=event_data, content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data


class TestDatabase:
    """Test database operations"""

    def test_database_connection(self, db):
        """Test database connection"""
        assert db.is_connected()
        assert db.events is not None

    def test_create_and_retrieve_event(self, db):
        """Test creating and retrieving an event"""
        from app.services import event_service

        event_data = EventCreate(
            title="Test DB Event",
            category="test",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            start_date=datetime.now(),
        )

        # Create event
        created_event = event_service.create_event(event_data)
        assert created_event.id is not None
        assert created_event.title == "Test DB Event"

        # Retrieve event
        retrieved_event = event_service.get_event(str(created_event.id))
        assert retrieved_event is not None
        assert retrieved_event.title == "Test DB Event"

    def test_nearby_events_search(self, db):
        """Test nearby events search"""
        from app.models import EventsNearbyQuery
        from app.services import event_service

        # Create test event
        event_data = EventCreate(
            title="Nearby Test Event",
            category="test",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),  # NYC
            start_date=datetime.now(),
        )

        event_service.create_event(event_data)

        # Search for nearby events
        query = EventsNearbyQuery(longitude=-74.0060, latitude=40.7128, radius_km=1)

        result = event_service.get_events_nearby(query)

        assert result["type"] == "FeatureCollection"
        assert len(result["features"]) >= 1

        feature = result["features"][0]
        assert feature["properties"]["title"] == "Nearby Test Event"
