import os
import sys
from datetime import datetime, timezone

import pytest

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import get_mongodb
from app.models import (
    EventCreate, EventLocation, VenueCreate, VenueAddress, UserCreate, UserProfile,
    ReviewCreate, ReviewUpdate
)
from app.services import get_review_service


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
    mongodb.reviews.delete_many({})


@pytest.fixture
def sample_event(db):
    """Create a sample event for testing"""
    event_data = EventCreate(
        title="Test Event",
        description="A test event for reviews",
        category="Music",
        location=EventLocation(coordinates=[-122.4194, 37.7749]),  # San Francisco
        start_date=datetime(2024, 6, 15, 19, 0),
        organizer="Test Organizer"
    )
    
    event_dict = event_data.model_dump()
    event_dict["created_at"] = datetime.now(timezone.utc)
    event_dict["updated_at"] = datetime.now(timezone.utc)
    
    result = db.events.insert_one(event_dict)
    event_dict["_id"] = result.inserted_id
    return str(result.inserted_id)


@pytest.fixture
def sample_venue(db):
    """Create a sample venue for testing"""
    venue_data = VenueCreate(
        name="Test Venue",
        location=EventLocation(coordinates=[-122.4194, 37.7749]),
        address=VenueAddress(
            street="123 Test St",
            city="San Francisco",
            state="CA",
            zip="94102",
            country="USA"
        ),
        capacity=100
    )
    
    venue_dict = venue_data.model_dump()
    venue_dict["created_at"] = datetime.now(timezone.utc)
    
    result = db.venues.insert_one(venue_dict)
    venue_dict["_id"] = result.inserted_id
    return str(result.inserted_id)


@pytest.fixture
def sample_user(db):
    """Create a sample user for testing"""
    user_data = UserCreate(
        email="test@example.com",
        profile=UserProfile(
            first_name="Test",
            last_name="User"
        )
    )
    
    user_dict = user_data.model_dump()
    user_dict["created_at"] = datetime.now(timezone.utc)
    
    result = db.users.insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    return str(result.inserted_id)


class TestReviewModels:
    """Test Review Pydantic models"""

    def test_review_create_valid_event_review(self):
        """Test creating a valid event review"""
        review_data = ReviewCreate(
            event_id="507f1f77bcf86cd799439011",
            user_id="507f1f77bcf86cd799439012",
            rating=5,
            comment="Great event!"
        )
        assert review_data.rating == 5
        assert review_data.comment == "Great event!"
        assert review_data.event_id is not None
        assert review_data.venue_id is None

    def test_review_create_valid_venue_review(self):
        """Test creating a valid venue review"""
        review_data = ReviewCreate(
            venue_id="507f1f77bcf86cd799439013",
            user_id="507f1f77bcf86cd799439012",
            rating=4,
            comment="Nice venue!"
        )
        assert review_data.rating == 4
        assert review_data.comment == "Nice venue!"
        assert review_data.venue_id is not None
        assert review_data.event_id is None

    def test_review_create_invalid_rating_low(self):
        """Test creating review with invalid low rating"""
        with pytest.raises(ValueError):
            ReviewCreate(
                event_id="507f1f77bcf86cd799439011",
                user_id="507f1f77bcf86cd799439012",
                rating=0,
                comment="Bad rating"
            )

    def test_review_create_invalid_rating_high(self):
        """Test creating review with invalid high rating"""
        with pytest.raises(ValueError):
            ReviewCreate(
                event_id="507f1f77bcf86cd799439011",
                user_id="507f1f77bcf86cd799439012",
                rating=6,
                comment="Bad rating"
            )

    def test_review_create_no_target(self):
        """Test creating review without event_id or venue_id"""
        with pytest.raises(ValueError):
            ReviewCreate(
                user_id="507f1f77bcf86cd799439012",
                rating=5,
                comment="No target"
            )

    def test_review_create_both_targets(self):
        """Test creating review with both event_id and venue_id"""
        with pytest.raises(ValueError):
            ReviewCreate(
                event_id="507f1f77bcf86cd799439011",
                venue_id="507f1f77bcf86cd799439013",
                user_id="507f1f77bcf86cd799439012",
                rating=5,
                comment="Both targets"
            )

    def test_review_create_long_comment(self):
        """Test creating review with comment too long"""
        with pytest.raises(ValueError):
            ReviewCreate(
                event_id="507f1f77bcf86cd799439011",
                user_id="507f1f77bcf86cd799439012",
                rating=5,
                comment="x" * 1001  # Too long
            )

    def test_review_update_valid(self):
        """Test updating review with valid data"""
        update_data = ReviewUpdate(
            rating=4,
            comment="Updated comment"
        )
        assert update_data.rating == 4
        assert update_data.comment == "Updated comment"


class TestReviewService:
    """Test ReviewService functionality"""

    def test_create_event_review(self, db, sample_event, sample_user):
        """Test creating an event review"""
        service = get_review_service()
        
        review_data = ReviewCreate(
            event_id=sample_event,
            user_id=sample_user,
            rating=5,
            comment="Amazing event!"
        )
        
        review = service.create_review(review_data)
        
        assert review.rating == 5
        assert review.comment == "Amazing event!"
        assert review.event_id is not None
        assert review.venue_id is None
        assert review.created_at is not None
        assert review.updated_at is not None

    def test_create_venue_review(self, db, sample_venue, sample_user):
        """Test creating a venue review"""
        service = get_review_service()
        
        review_data = ReviewCreate(
            venue_id=sample_venue,
            user_id=sample_user,
            rating=4,
            comment="Great venue!"
        )
        
        review = service.create_review(review_data)
        
        assert review.rating == 4
        assert review.comment == "Great venue!"
        assert review.venue_id is not None
        assert review.event_id is None

    def test_get_review_by_id(self, db, sample_event, sample_user):
        """Test getting review by ID"""
        service = get_review_service()
        
        # Create a review
        review_data = ReviewCreate(
            event_id=sample_event,
            user_id=sample_user,
            rating=5,
            comment="Test review"
        )
        created_review = service.create_review(review_data)
        
        # Get the review
        retrieved_review = service.get_review(str(created_review.id))
        
        assert retrieved_review is not None
        assert retrieved_review.rating == 5
        assert retrieved_review.comment == "Test review"

    def test_get_review_invalid_id(self, db):
        """Test getting review with invalid ID"""
        service = get_review_service()
        
        review = service.get_review("invalid_id")
        assert review is None

    def test_get_reviews_by_event(self, db, sample_event, sample_user):
        """Test getting reviews by event ID"""
        service = get_review_service()
        
        # Create multiple reviews for the event
        for i in range(3):
            review_data = ReviewCreate(
                event_id=sample_event,
                user_id=sample_user,
                rating=3 + i,  # This will give ratings 3, 4, 5
                comment=f"Review {i+1}"
            )
            service.create_review(review_data)
        
        # Get reviews for the event
        result = service.get_reviews_by_event(sample_event)
        
        assert len(result["reviews"]) == 3
        assert result["has_more"] is False
        assert result["offset"] == 3

    def test_get_reviews_by_venue(self, db, sample_venue, sample_user):
        """Test getting reviews by venue ID"""
        service = get_review_service()
        
        # Create multiple reviews for the venue
        for i in range(2):
            review_data = ReviewCreate(
                venue_id=sample_venue,
                user_id=sample_user,
                rating=3 + i,
                comment=f"Venue review {i+1}"
            )
            service.create_review(review_data)
        
        # Get reviews for the venue
        result = service.get_reviews_by_venue(sample_venue)
        
        assert len(result["reviews"]) == 2
        assert result["has_more"] is False
        assert result["offset"] == 2

    def test_get_reviews_by_user(self, db, sample_event, sample_venue, sample_user):
        """Test getting reviews by user ID"""
        service = get_review_service()
        
        # Create reviews for different targets
        event_review = ReviewCreate(
            event_id=sample_event,
            user_id=sample_user,
            rating=5,
            comment="Event review"
        )
        service.create_review(event_review)
        
        venue_review = ReviewCreate(
            venue_id=sample_venue,
            user_id=sample_user,
            rating=4,
            comment="Venue review"
        )
        service.create_review(venue_review)
        
        # Get reviews by user
        result = service.get_reviews_by_user(sample_user)
        
        assert len(result["reviews"]) == 2
        assert result["has_more"] is False
        assert result["offset"] == 2

    def test_update_review(self, db, sample_event, sample_user):
        """Test updating a review"""
        service = get_review_service()
        
        # Create a review
        review_data = ReviewCreate(
            event_id=sample_event,
            user_id=sample_user,
            rating=3,
            comment="Original comment"
        )
        created_review = service.create_review(review_data)
        
        # Update the review
        update_data = ReviewUpdate(
            rating=5,
            comment="Updated comment"
        )
        updated_review = service.update_review(str(created_review.id), update_data)
        
        assert updated_review is not None
        assert updated_review.rating == 5
        assert updated_review.comment == "Updated comment"
        assert updated_review.updated_at > created_review.updated_at

    def test_delete_review(self, db, sample_event, sample_user):
        """Test deleting a review"""
        service = get_review_service()
        
        # Create a review
        review_data = ReviewCreate(
            event_id=sample_event,
            user_id=sample_user,
            rating=4,
            comment="To be deleted"
        )
        created_review = service.create_review(review_data)
        
        # Delete the review
        deleted = service.delete_review(str(created_review.id))
        assert deleted is True
        
        # Verify it's deleted
        retrieved_review = service.get_review(str(created_review.id))
        assert retrieved_review is None

    def test_get_review_stats_by_event(self, db, sample_event, sample_user):
        """Test getting review statistics for an event"""
        service = get_review_service()
        
        # Create reviews with different ratings
        ratings = [5, 4, 5, 3, 4]
        for rating in ratings:
            review_data = ReviewCreate(
                event_id=sample_event,
                user_id=sample_user,
                rating=rating,
                comment=f"Rating {rating}"
            )
            service.create_review(review_data)
        
        # Get statistics
        stats = service.get_review_stats_by_event(sample_event)
        
        assert stats["total_reviews"] == 5
        assert stats["average_rating"] == 4.2
        assert stats["rating_distribution"]["5"] == 2
        assert stats["rating_distribution"]["4"] == 2
        assert stats["rating_distribution"]["3"] == 1

    def test_get_review_stats_by_venue(self, db, sample_venue, sample_user):
        """Test getting review statistics for a venue"""
        service = get_review_service()
        
        # Create reviews with different ratings
        ratings = [5, 5, 4, 2]
        for rating in ratings:
            review_data = ReviewCreate(
                venue_id=sample_venue,
                user_id=sample_user,
                rating=rating,
                comment=f"Venue rating {rating}"
            )
            service.create_review(review_data)
        
        # Get statistics
        stats = service.get_review_stats_by_venue(sample_venue)
        
        assert stats["total_reviews"] == 4
        assert stats["average_rating"] == 4.0
        assert stats["rating_distribution"]["5"] == 2
        assert stats["rating_distribution"]["4"] == 1
        assert stats["rating_distribution"]["2"] == 1

    def test_search_reviews(self, db, sample_event, sample_user):
        """Test searching reviews by comment text"""
        service = get_review_service()
        
        # Create reviews with different comments
        comments = ["Amazing event!", "Great music", "Amazing venue", "Good food"]
        for comment in comments:
            review_data = ReviewCreate(
                event_id=sample_event,
                user_id=sample_user,
                rating=4,
                comment=comment
            )
            service.create_review(review_data)
        
        # Search for "amazing"
        result = service.search_reviews("amazing")
        
        # Should find reviews containing "amazing" (case insensitive)
        assert len(result["reviews"]) >= 2
        assert any("amazing" in review.comment.lower() for review in result["reviews"])

    def test_pagination(self, db, sample_event, sample_user):
        """Test pagination functionality"""
        service = get_review_service()
        
        # Create 5 reviews
        for i in range(5):
            review_data = ReviewCreate(
                event_id=sample_event,
                user_id=sample_user,
                rating=4,
                comment=f"Review {i+1}"
            )
            service.create_review(review_data)
        
        # Test first page
        result1 = service.get_reviews_by_event(sample_event, skip=0, limit=3)
        assert len(result1["reviews"]) == 3
        assert result1["has_more"] is True
        assert result1["offset"] == 3
        
        # Test second page
        result2 = service.get_reviews_by_event(sample_event, skip=3, limit=3)
        assert len(result2["reviews"]) == 2
        assert result2["has_more"] is False
        assert result2["offset"] == 5

    def test_invalid_object_ids(self, db):
        """Test handling of invalid ObjectIds"""
        service = get_review_service()
        
        # Test with invalid event ID
        result = service.get_reviews_by_event("invalid_id")
        assert result["reviews"] == []
        assert result["has_more"] is False
        assert result["offset"] == 0
        
        # Test with invalid venue ID
        result = service.get_reviews_by_venue("invalid_id")
        assert result["reviews"] == []
        assert result["has_more"] is False
        assert result["offset"] == 0
        
        # Test with invalid user ID
        result = service.get_reviews_by_user("invalid_id")
        assert result["reviews"] == []
        assert result["has_more"] is False
        assert result["offset"] == 0


class TestReviewValidation:
    """Test review validation scenarios"""

    def test_review_validation_rating_bounds(self, db, sample_event, sample_user):
        """Test that rating bounds are enforced by JSON Schema"""
        service = get_review_service()
        
        # Test rating too low (should be caught by Pydantic before reaching MongoDB)
        with pytest.raises(ValueError):
            review_data = ReviewCreate(
                event_id=sample_event,
                user_id=sample_user,
                rating=0,
                comment="Invalid rating"
            )
            service.create_review(review_data)
        
        # Test rating too high (should be caught by Pydantic before reaching MongoDB)
        with pytest.raises(ValueError):
            review_data = ReviewCreate(
                event_id=sample_event,
                user_id=sample_user,
                rating=6,
                comment="Invalid rating"
            )
            service.create_review(review_data)

    def test_review_validation_required_fields(self, db, sample_event, sample_user):
        """Test that required fields are enforced"""
        service = get_review_service()
        
        # Test missing user_id
        with pytest.raises(ValueError):
            review_data = ReviewCreate(
                event_id=sample_event,
                rating=5,
                comment="Missing user_id"
            )
            service.create_review(review_data)
        
        # Test missing rating
        with pytest.raises(ValueError):
            review_data = ReviewCreate(
                event_id=sample_event,
                user_id=sample_user,
                comment="Missing rating"
            )
            service.create_review(review_data)


if __name__ == "__main__":
    pytest.main([__file__])

