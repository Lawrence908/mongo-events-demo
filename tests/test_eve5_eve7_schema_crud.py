import os
import sys
from datetime import datetime

import pytest

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import get_mongodb
from app.models import (
    EventCreate, EventLocation, EventUpdate,
    VenueCreate, VenueUpdate, VenueAddress, VenueContact,
    UserCreate, UserUpdate, UserProfile, UserPreferences,
    CheckinCreate, CheckinUpdate
)


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
    mongodb.venues.delete_many({})
    mongodb.users.delete_many({})
    mongodb.checkins.delete_many({})


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


class TestEventServiceCRUD:
    """Test EventService CRUD operations"""

    def test_create_event_happy_path(self, db):
        """Test creating an event successfully"""
        from app.services import get_event_service
        
        event_data = EventCreate(
            title="Test Event",
            category="conference",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            start_date=datetime.now(),
            description="A test event",
            organizer="Test Organizer"
        )
        
        service = get_event_service()
        created_event = service.create_event(event_data)
        
        assert created_event.id is not None
        assert created_event.title == "Test Event"
        assert created_event.category == "conference"
        assert created_event.organizer == "Test Organizer"
        assert created_event.created_at is not None
        assert created_event.updated_at is not None

    def test_get_event_happy_path(self, db):
        """Test retrieving an event successfully"""
        from app.services import get_event_service
        
        # Create an event first
        event_data = EventCreate(
            title="Test Event",
            category="conference",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            start_date=datetime.now()
        )
        
        service = get_event_service()
        created_event = service.create_event(event_data)
        
        # Retrieve the event
        retrieved_event = service.get_event(str(created_event.id))
        
        assert retrieved_event is not None
        assert retrieved_event.id == created_event.id
        assert retrieved_event.title == "Test Event"

    def test_get_event_invalid_objectid(self, db):
        """Test retrieving event with invalid ObjectId"""
        from app.services import get_event_service
        
        service = get_event_service()
        result = service.get_event("invalid_id")
        
        assert result is None

    def test_get_event_not_found(self, db):
        """Test retrieving non-existent event"""
        from app.services import get_event_service
        from bson import ObjectId
        
        service = get_event_service()
        result = service.get_event(str(ObjectId()))
        
        assert result is None

    def test_update_event_happy_path(self, db):
        """Test updating an event successfully"""
        from app.services import get_event_service
        
        # Create an event first
        event_data = EventCreate(
            title="Original Title",
            category="conference",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            start_date=datetime.now()
        )
        
        service = get_event_service()
        created_event = service.create_event(event_data)
        
        # Update the event
        update_data = EventUpdate(
            title="Updated Title",
            description="Updated description"
        )
        
        updated_event = service.update_event(str(created_event.id), update_data)
        
        assert updated_event is not None
        assert updated_event.title == "Updated Title"
        assert updated_event.description == "Updated description"
        assert updated_event.updated_at > created_event.updated_at

    def test_update_event_partial_update(self, db):
        """Test partial update of an event"""
        from app.services import get_event_service
        
        # Create an event first
        event_data = EventCreate(
            title="Original Title",
            category="conference",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            start_date=datetime.now(),
            description="Original description"
        )
        
        service = get_event_service()
        created_event = service.create_event(event_data)
        
        # Update only the title
        update_data = EventUpdate(title="Updated Title")
        
        updated_event = service.update_event(str(created_event.id), update_data)
        
        assert updated_event is not None
        assert updated_event.title == "Updated Title"
        assert updated_event.description == "Original description"  # Should remain unchanged
        assert updated_event.category == "conference"  # Should remain unchanged

    def test_update_event_invalid_objectid(self, db):
        """Test updating event with invalid ObjectId"""
        from app.services import get_event_service
        
        service = get_event_service()
        update_data = EventUpdate(title="Updated Title")
        result = service.update_event("invalid_id", update_data)
        
        assert result is None

    def test_update_event_not_found(self, db):
        """Test updating non-existent event"""
        from app.services import get_event_service
        from bson import ObjectId
        
        service = get_event_service()
        update_data = EventUpdate(title="Updated Title")
        result = service.update_event(str(ObjectId()), update_data)
        
        assert result is None

    def test_delete_event_happy_path(self, db):
        """Test deleting an event successfully"""
        from app.services import get_event_service
        
        # Create an event first
        event_data = EventCreate(
            title="Test Event",
            category="conference",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            start_date=datetime.now()
        )
        
        service = get_event_service()
        created_event = service.create_event(event_data)
        
        # Delete the event
        result = service.delete_event(str(created_event.id))
        
        assert result is True
        
        # Verify event is deleted
        deleted_event = service.get_event(str(created_event.id))
        assert deleted_event is None

    def test_delete_event_invalid_objectid(self, db):
        """Test deleting event with invalid ObjectId"""
        from app.services import get_event_service
        
        service = get_event_service()
        result = service.delete_event("invalid_id")
        
        assert result is False

    def test_delete_event_not_found(self, db):
        """Test deleting non-existent event"""
        from app.services import get_event_service
        from bson import ObjectId
        
        service = get_event_service()
        result = service.delete_event(str(ObjectId()))
        
        assert result is False


class TestVenueServiceCRUD:
    """Test VenueService CRUD operations"""

    def test_create_venue_happy_path(self, db):
        """Test creating a venue successfully"""
        from app.services import get_venue_service
        
        venue_data = VenueCreate(
            name="Test Venue",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            address=VenueAddress(
                street="123 Test St",
                city="New York",
                state="NY",
                zip="10001",
                country="USA"
            ),
            capacity=100,
            amenities=["WiFi", "Parking"]
        )
        
        service = get_venue_service()
        created_venue = service.create_venue(venue_data)
        
        assert created_venue.id is not None
        assert created_venue.name == "Test Venue"
        assert created_venue.capacity == 100
        assert "WiFi" in created_venue.amenities
        assert created_venue.created_at is not None

    def test_get_venue_happy_path(self, db):
        """Test retrieving a venue successfully"""
        from app.services import get_venue_service
        
        # Create a venue first
        venue_data = VenueCreate(
            name="Test Venue",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            address=VenueAddress(
                street="123 Test St",
                city="New York",
                state="NY",
                zip="10001",
                country="USA"
            )
        )
        
        service = get_venue_service()
        created_venue = service.create_venue(venue_data)
        
        # Retrieve the venue
        retrieved_venue = service.get_venue(str(created_venue.id))
        
        assert retrieved_venue is not None
        assert retrieved_venue.id == created_venue.id
        assert retrieved_venue.name == "Test Venue"

    def test_get_venue_invalid_objectid(self, db):
        """Test retrieving venue with invalid ObjectId"""
        from app.services import get_venue_service
        
        service = get_venue_service()
        result = service.get_venue("invalid_id")
        
        assert result is None

    def test_update_venue_happy_path(self, db):
        """Test updating a venue successfully"""
        from app.services import get_venue_service
        
        # Create a venue first
        venue_data = VenueCreate(
            name="Original Name",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            address=VenueAddress(
                street="123 Test St",
                city="New York",
                state="NY",
                zip="10001",
                country="USA"
            )
        )
        
        service = get_venue_service()
        created_venue = service.create_venue(venue_data)
        
        # Update the venue
        update_data = VenueUpdate(
            name="Updated Name",
            capacity=200
        )
        
        updated_venue = service.update_venue(str(created_venue.id), update_data)
        
        assert updated_venue is not None
        assert updated_venue.name == "Updated Name"
        assert updated_venue.capacity == 200

    def test_delete_venue_happy_path(self, db):
        """Test deleting a venue successfully"""
        from app.services import get_venue_service
        
        # Create a venue first
        venue_data = VenueCreate(
            name="Test Venue",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            address=VenueAddress(
                street="123 Test St",
                city="New York",
                state="NY",
                zip="10001",
                country="USA"
            )
        )
        
        service = get_venue_service()
        created_venue = service.create_venue(venue_data)
        
        # Delete the venue
        result = service.delete_venue(str(created_venue.id))
        
        assert result is True
        
        # Verify venue is deleted
        deleted_venue = service.get_venue(str(created_venue.id))
        assert deleted_venue is None


class TestUserServiceCRUD:
    """Test UserService CRUD operations"""

    def test_create_user_happy_path(self, db):
        """Test creating a user successfully"""
        from app.services import get_user_service
        
        user_data = UserCreate(
            email="test@example.com",
            profile=UserProfile(
                first_name="John",
                last_name="Doe",
                preferences=UserPreferences(
                    categories=["tech", "music"],
                    location=EventLocation(coordinates=[-74.0060, 40.7128]),
                    radius_km=10.0
                )
            )
        )
        
        service = get_user_service()
        created_user = service.create_user(user_data)
        
        assert created_user.id is not None
        assert created_user.email == "test@example.com"
        assert created_user.profile.first_name == "John"
        assert created_user.profile.last_name == "Doe"
        assert created_user.created_at is not None

    def test_get_user_happy_path(self, db):
        """Test retrieving a user successfully"""
        from app.services import get_user_service
        
        # Create a user first
        user_data = UserCreate(
            email="test@example.com",
            profile=UserProfile(
                first_name="John",
                last_name="Doe"
            )
        )
        
        service = get_user_service()
        created_user = service.create_user(user_data)
        
        # Retrieve the user
        retrieved_user = service.get_user(str(created_user.id))
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == "test@example.com"

    def test_get_user_by_email(self, db):
        """Test retrieving user by email"""
        from app.services import get_user_service
        
        # Create a user first
        user_data = UserCreate(
            email="test@example.com",
            profile=UserProfile(
                first_name="John",
                last_name="Doe"
            )
        )
        
        service = get_user_service()
        created_user = service.create_user(user_data)
        
        # Retrieve the user by email
        retrieved_user = service.get_user_by_email("test@example.com")
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == "test@example.com"

    def test_update_user_happy_path(self, db):
        """Test updating a user successfully"""
        from app.services import get_user_service
        
        # Create a user first
        user_data = UserCreate(
            email="test@example.com",
            profile=UserProfile(
                first_name="John",
                last_name="Doe"
            )
        )
        
        service = get_user_service()
        created_user = service.create_user(user_data)
        
        # Update the user
        update_data = UserUpdate(
            profile=UserProfile(
                first_name="Jane",
                last_name="Smith"
            )
        )
        
        updated_user = service.update_user(str(created_user.id), update_data)
        
        assert updated_user is not None
        assert updated_user.profile.first_name == "Jane"
        assert updated_user.profile.last_name == "Smith"

    def test_delete_user_happy_path(self, db):
        """Test deleting a user successfully"""
        from app.services import get_user_service
        
        # Create a user first
        user_data = UserCreate(
            email="test@example.com",
            profile=UserProfile(
                first_name="John",
                last_name="Doe"
            )
        )
        
        service = get_user_service()
        created_user = service.create_user(user_data)
        
        # Delete the user
        result = service.delete_user(str(created_user.id))
        
        assert result is True
        
        # Verify user is deleted
        deleted_user = service.get_user(str(created_user.id))
        assert deleted_user is None


class TestCheckinServiceCRUD:
    """Test CheckinService CRUD operations"""

    def test_create_checkin_happy_path(self, db):
        """Test creating a checkin successfully"""
        from app.services import get_checkin_service, get_event_service, get_user_service
        from bson import ObjectId
        
        # Create an event and user first
        event_data = EventCreate(
            title="Test Event",
            category="conference",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            start_date=datetime.now()
        )
        
        user_data = UserCreate(
            email="test@example.com",
            profile=UserProfile(
                first_name="John",
                last_name="Doe"
            )
        )
        
        event_service = get_event_service()
        user_service = get_user_service()
        checkin_service = get_checkin_service()
        
        created_event = event_service.create_event(event_data)
        created_user = user_service.create_user(user_data)
        
        # Create a checkin
        checkin_data = CheckinCreate(
            event_id=created_event.id,
            user_id=created_user.id,
            qr_code="QR123456",
            ticket_tier="VIP"
        )
        
        created_checkin = checkin_service.create_checkin(checkin_data)
        
        assert created_checkin.id is not None
        assert created_checkin.event_id == created_event.id
        assert created_checkin.user_id == created_user.id
        assert created_checkin.qr_code == "QR123456"
        assert created_checkin.ticket_tier == "VIP"
        assert created_checkin.check_in_time is not None

    def test_get_checkin_happy_path(self, db):
        """Test retrieving a checkin successfully"""
        from app.services import get_checkin_service, get_event_service, get_user_service
        
        # Create an event and user first
        event_data = EventCreate(
            title="Test Event",
            category="conference",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            start_date=datetime.now()
        )
        
        user_data = UserCreate(
            email="test@example.com",
            profile=UserProfile(
                first_name="John",
                last_name="Doe"
            )
        )
        
        event_service = get_event_service()
        user_service = get_user_service()
        checkin_service = get_checkin_service()
        
        created_event = event_service.create_event(event_data)
        created_user = user_service.create_user(user_data)
        
        # Create a checkin
        checkin_data = CheckinCreate(
            event_id=created_event.id,
            user_id=created_user.id,
            qr_code="QR123456"
        )
        
        created_checkin = checkin_service.create_checkin(checkin_data)
        
        # Retrieve the checkin
        retrieved_checkin = checkin_service.get_checkin(str(created_checkin.id))
        
        assert retrieved_checkin is not None
        assert retrieved_checkin.id == created_checkin.id
        assert retrieved_checkin.qr_code == "QR123456"

    def test_get_checkins_by_event(self, db):
        """Test retrieving checkins by event"""
        from app.services import get_checkin_service, get_event_service, get_user_service
        
        # Create an event and users first
        event_data = EventCreate(
            title="Test Event",
            category="conference",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            start_date=datetime.now()
        )
        
        event_service = get_event_service()
        user_service = get_user_service()
        checkin_service = get_checkin_service()
        
        created_event = event_service.create_event(event_data)
        
        # Create multiple users and checkins
        for i in range(3):
            user_data = UserCreate(
                email=f"user{i}@example.com",
                profile=UserProfile(
                    first_name=f"User{i}",
                    last_name="Doe"
                )
            )
            created_user = user_service.create_user(user_data)
            
            checkin_data = CheckinCreate(
                event_id=created_event.id,
                user_id=created_user.id,
                qr_code=f"QR{i}123456"
            )
            checkin_service.create_checkin(checkin_data)
        
        # Get checkins for the event
        result = checkin_service.get_checkins_by_event(str(created_event.id))
        
        assert len(result["checkins"]) == 3
        assert result["has_more"] is False

    def test_get_checkins_by_user(self, db):
        """Test retrieving checkins by user"""
        from app.services import get_checkin_service, get_event_service, get_user_service
        
        # Create a user and events first
        user_data = UserCreate(
            email="test@example.com",
            profile=UserProfile(
                first_name="John",
                last_name="Doe"
            )
        )
        
        event_service = get_event_service()
        user_service = get_user_service()
        checkin_service = get_checkin_service()
        
        created_user = user_service.create_user(user_data)
        
        # Create multiple events and checkins
        for i in range(3):
            event_data = EventCreate(
                title=f"Test Event {i}",
                category="conference",
                location=EventLocation(coordinates=[-74.0060, 40.7128]),
                start_date=datetime.now()
            )
            created_event = event_service.create_event(event_data)
            
            checkin_data = CheckinCreate(
                event_id=created_event.id,
                user_id=created_user.id,
                qr_code=f"QR{i}123456"
            )
            checkin_service.create_checkin(checkin_data)
        
        # Get checkins for the user
        result = checkin_service.get_checkins_by_user(str(created_user.id))
        
        assert len(result["checkins"]) == 3
        assert result["has_more"] is False

    def test_update_checkin_happy_path(self, db):
        """Test updating a checkin successfully"""
        from app.services import get_checkin_service, get_event_service, get_user_service
        
        # Create an event and user first
        event_data = EventCreate(
            title="Test Event",
            category="conference",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            start_date=datetime.now()
        )
        
        user_data = UserCreate(
            email="test@example.com",
            profile=UserProfile(
                first_name="John",
                last_name="Doe"
            )
        )
        
        event_service = get_event_service()
        user_service = get_user_service()
        checkin_service = get_checkin_service()
        
        created_event = event_service.create_event(event_data)
        created_user = user_service.create_user(user_data)
        
        # Create a checkin
        checkin_data = CheckinCreate(
            event_id=created_event.id,
            user_id=created_user.id,
            qr_code="QR123456",
            ticket_tier="General"
        )
        
        created_checkin = checkin_service.create_checkin(checkin_data)
        
        # Update the checkin
        update_data = CheckinUpdate(
            ticket_tier="VIP"
        )
        
        updated_checkin = checkin_service.update_checkin(str(created_checkin.id), update_data)
        
        assert updated_checkin is not None
        assert updated_checkin.ticket_tier == "VIP"
        assert updated_checkin.qr_code == "QR123456"  # Should remain unchanged

    def test_delete_checkin_happy_path(self, db):
        """Test deleting a checkin successfully"""
        from app.services import get_checkin_service, get_event_service, get_user_service
        
        # Create an event and user first
        event_data = EventCreate(
            title="Test Event",
            category="conference",
            location=EventLocation(coordinates=[-74.0060, 40.7128]),
            start_date=datetime.now()
        )
        
        user_data = UserCreate(
            email="test@example.com",
            profile=UserProfile(
                first_name="John",
                last_name="Doe"
            )
        )
        
        event_service = get_event_service()
        user_service = get_user_service()
        checkin_service = get_checkin_service()
        
        created_event = event_service.create_event(event_data)
        created_user = user_service.create_user(user_data)
        
        # Create a checkin
        checkin_data = CheckinCreate(
            event_id=created_event.id,
            user_id=created_user.id,
            qr_code="QR123456"
        )
        
        created_checkin = checkin_service.create_checkin(checkin_data)
        
        # Delete the checkin
        result = checkin_service.delete_checkin(str(created_checkin.id))
        
        assert result is True
        
        # Verify checkin is deleted
        deleted_checkin = checkin_service.get_checkin(str(created_checkin.id))
        assert deleted_checkin is None
