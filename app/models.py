from datetime import datetime, timezone
from typing import Any, Optional, List, Literal

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic_core import core_schema

from .config import Config


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2"""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    core_schema.chain_schema(
                        [
                            core_schema.str_schema(),
                            core_schema.no_info_plain_validator_function(cls.validate),
                        ]
                    ),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class EventAddress(BaseModel):
    """Event address information"""
    street: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    zip: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=1, max_length=100)


class EventLocation(BaseModel):
    """Geographic location with coordinates"""

    type: str = Field(default="Point", description="GeoJSON type")
    coordinates: list[float] = Field(..., description="[longitude, latitude]")

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, v):
        if len(v) != 2:
            raise ValueError("Coordinates must be [longitude, latitude]")
        lng, lat = v
        if not (-180 <= lng <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v


class EventTicket(BaseModel):
    """Event ticket information"""
    tier: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., ge=0)
    available: int = Field(..., ge=0)
    sold: int = Field(..., ge=0)


class EventAttendee(BaseModel):
    """Event attendee information"""
    userId: PyObjectId
    checkedIn: bool = Field(default=False)
    checkInTime: Optional[datetime] = None


class EventMetadata(BaseModel):
    """Event metadata for custom attributes"""
    virtual: Optional[bool] = None
    recurring: Optional[bool] = None
    ageRestriction: Optional[str] = None
    dressCode: Optional[str] = None


class EventBase(BaseModel):
    """Base event model"""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field(..., min_length=1, max_length=50)
    eventType: Literal["inPerson", "virtual", "hybrid", "recurring"] = Field(..., description="Polymorphic discriminator")
    schemaVersion: str = Field(default="1.0", description="Schema versioning")
    location: EventLocation
    address: Optional[EventAddress] = None
    directionsUrl: Optional[str] = Field(None, max_length=500, description="Google Maps directions URL")
    venueId: Optional[PyObjectId] = None
    venueReference: Optional[dict] = Field(None, description="Extended reference data for performance")
    startDate: datetime
    endDate: Optional[datetime] = None
    organizer: Optional[str] = Field(None, max_length=100)
    maxAttendees: Optional[int] = Field(None, gt=0)
    currentAttendees: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    isFree: Optional[bool] = Field(None)
    status: Optional[Literal["draft", "published", "cancelled", "completed"]] = Field(None)
    tickets: Optional[List[EventTicket]] = None
    attendees: Optional[List[EventAttendee]] = None
    tags: List[str] = Field(default_factory=list)
    
    # Polymorphic type-specific fields
    virtualDetails: Optional[dict] = Field(None, description="Virtual event specific details")
    recurringDetails: Optional[dict] = Field(None, description="Recurring event specific details") 
    hybridDetails: Optional[dict] = Field(None, description="Hybrid event specific details")
    metadata: Optional[dict] = Field(None, description="General metadata")
    
    # Computed pattern fields
    computedStats: Optional[dict] = Field(None, description="Pre-calculated statistics")

    @field_validator("endDate")
    @classmethod
    def validate_endDate(cls, v, info):
        if v and info.data.get("startDate") and v <= info.data["startDate"]:
            raise ValueError("End date must be after start date")
        return v


class EventCreate(EventBase):
    """Model for creating events"""

    pass


class EventUpdate(BaseModel):
    """Model for updating events"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    eventType: Optional[Literal["inPerson", "virtual", "hybrid", "recurring"]] = None
    location: Optional[EventLocation] = None
    address: Optional[EventAddress] = None
    directionsUrl: Optional[str] = Field(None, max_length=500, description="Google Maps directions URL")
    venueId: Optional[PyObjectId] = None
    venueReference: Optional[dict] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    organizer: Optional[str] = Field(None, max_length=100)
    maxAttendees: Optional[int] = Field(None, gt=0)
    currentAttendees: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    isFree: Optional[bool] = None
    status: Optional[Literal["draft", "published", "cancelled", "completed"]] = None
    tickets: Optional[List[EventTicket]] = None
    attendees: Optional[List[EventAttendee]] = None
    tags: Optional[List[str]] = None
    virtualDetails: Optional[dict] = None
    recurringDetails: Optional[dict] = None
    hybridDetails: Optional[dict] = None
    metadata: Optional[dict] = None
    computedStats: Optional[dict] = None


class Event(EventBase):
    """Complete event model with database fields"""

    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    score: Optional[float] = Field(None, description="Text search relevance score")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


# Venue Models
class VenueAddress(BaseModel):
    """Venue address information"""
    street: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    zip: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=1, max_length=100)


class VenueContact(BaseModel):
    """Venue contact information"""
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)


class VenueBase(BaseModel):
    """Base venue model"""
    name: str = Field(..., min_length=1, max_length=200)
    venueType: Literal["conferenceCenter", "park", "restaurant", "virtualSpace", "stadium", "theater"] = Field(..., description="Polymorphic discriminator")
    schemaVersion: str = Field(default="1.0", description="Schema versioning")
    location: EventLocation
    address: VenueAddress
    capacity: Optional[int] = Field(None, gt=0)
    amenities: List[str] = Field(default_factory=list)
    contact: Optional[VenueContact] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    reviewCount: Optional[int] = Field(None, ge=0)
    
    # Polymorphic type-specific fields
    conferenceCenterDetails: Optional[dict] = Field(None, description="Conference center specific details")
    parkDetails: Optional[dict] = Field(None, description="Park specific details")
    virtualSpaceDetails: Optional[dict] = Field(None, description="Virtual space specific details")
    
    # Computed pattern fields
    computedStats: Optional[dict] = Field(None, description="Pre-calculated statistics")


class VenueCreate(VenueBase):
    """Model for creating venues"""
    pass


class VenueUpdate(BaseModel):
    """Model for updating venues"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    location: Optional[EventLocation] = None
    address: Optional[VenueAddress] = None
    capacity: Optional[int] = Field(None, gt=0)
    amenities: Optional[List[str]] = None
    contact: Optional[VenueContact] = None


class Venue(VenueBase):
    """Complete venue model with database fields"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


# User Models
class UserPreferences(BaseModel):
    """User preferences"""
    categories: List[str] = Field(default_factory=list)
    location: Optional[EventLocation] = None
    radiusKm: Optional[float] = Field(None, ge=0.1, le=1000)


class UserProfile(BaseModel):
    """User profile information"""
    firstName: str = Field(..., min_length=1, max_length=100)
    lastName: str = Field(..., min_length=1, max_length=100)
    preferences: Optional[UserPreferences] = None


class UserBase(BaseModel):
    """Base user model"""
    email: str = Field(..., min_length=1, max_length=255)
    schemaVersion: str = Field(default="1.0", description="Schema versioning")
    profile: UserProfile


class UserCreate(UserBase):
    """Model for creating users"""
    pass


class UserUpdate(BaseModel):
    """Model for updating users"""
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    profile: Optional[UserProfile] = None


class User(UserBase):
    """Complete user model with database fields"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    lastLogin: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


# Checkin Models
class CheckinMetadata(BaseModel):
    """Check-in metadata for additional context"""
    deviceInfo: Optional[str] = Field(None, max_length=200, description="Mobile device or browser info")
    ipAddress: Optional[str] = Field(None, max_length=45, description="IP address for security/analytics")
    staffVerified: Optional[bool] = Field(None, description="Manual verification by staff")


class CheckinBase(BaseModel):
    """Base checkin model"""
    eventId: PyObjectId
    userId: PyObjectId
    venueId: Optional[PyObjectId] = Field(None, description="Reference to venues (denormalized for analytics)")
    qrCode: str = Field(..., min_length=1, max_length=100)
    schemaVersion: str = Field(default="1.0", description="Schema versioning")
    ticketTier: Optional[str] = Field(None, max_length=50)
    checkInMethod: Optional[str] = Field(None, max_length=50, description="qr_code, manual, mobile_app")
    location: Optional[EventLocation] = None
    metadata: Optional[CheckinMetadata] = None


class CheckinCreate(CheckinBase):
    """Model for creating checkins"""
    pass


class CheckinUpdate(BaseModel):
    """Model for updating checkins"""
    qr_code: Optional[str] = Field(None, min_length=1, max_length=100)
    ticketTier: Optional[str] = Field(None, max_length=50)
    check_in_method: Optional[str] = Field(None, max_length=50)
    location: Optional[EventLocation] = None
    metadata: Optional[CheckinMetadata] = None


class Checkin(CheckinBase):
    """Complete checkin model with database fields"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    checkInTime: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


# Review Models
class ReviewBase(BaseModel):
    """Base review model"""
    eventId: Optional[PyObjectId] = Field(None, description="Reference to events collection (if reviewing event)")
    venueId: Optional[PyObjectId] = Field(None, description="Reference to venues collection (if reviewing venue)")
    userId: PyObjectId = Field(..., description="Reference to users collection")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = Field(None, max_length=1000, description="Review comment text")
    schemaVersion: str = Field(default="1.0", description="Schema versioning")

    @model_validator(mode="after")
    def validate_review_target(self):
        """Ensure at least one of event_id or venue_id is provided"""
        if not self.eventId and not self.venueId:
            raise ValueError("Either event_id or venue_id must be provided")
        if self.eventId and self.venueId:
            raise ValueError("Cannot review both event and venue in the same review")
        return self


class ReviewCreate(ReviewBase):
    """Model for creating reviews"""
    pass


class ReviewUpdate(BaseModel):
    """Model for updating reviews"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)


class Review(ReviewBase):
    """Complete review model with database fields"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


# (Removed duplicate alternative Review models with review_text/title fields to match tests using 'comment')


# Query Models
class EventsNearbyQuery(BaseModel):
    """Query parameters for nearby events"""

    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    radius_km: float = Field(default=10, gt=0, le=20000)
    limit: int = Field(default=50, gt=0, le=Config.MAX_EVENTS_LIMIT)
