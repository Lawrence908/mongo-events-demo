from datetime import datetime
from typing import Any, Optional, List, Literal

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import core_schema


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
    user_id: PyObjectId
    checked_in: bool = Field(default=False)
    check_in_time: Optional[datetime] = None


class EventMetadata(BaseModel):
    """Event metadata for custom attributes"""
    virtual: Optional[bool] = None
    recurring: Optional[bool] = None
    age_restriction: Optional[str] = None
    dress_code: Optional[str] = None


class EventBase(BaseModel):
    """Base event model"""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field(..., min_length=1, max_length=50)
    location: EventLocation
    venue_id: Optional[PyObjectId] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    organizer: Optional[str] = Field(None, max_length=100)
    max_attendees: Optional[int] = Field(None, gt=0)
    tickets: Optional[List[EventTicket]] = None
    attendees: Optional[List[EventAttendee]] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Optional[EventMetadata] = None

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v, info):
        if v and info.data.get("start_date") and v <= info.data["start_date"]:
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
    location: Optional[EventLocation] = None
    venue_id: Optional[PyObjectId] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    organizer: Optional[str] = Field(None, max_length=100)
    max_attendees: Optional[int] = Field(None, gt=0)
    tickets: Optional[List[EventTicket]] = None
    attendees: Optional[List[EventAttendee]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[EventMetadata] = None


class Event(EventBase):
    """Complete event model with database fields"""

    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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
    location: EventLocation
    address: VenueAddress
    capacity: Optional[int] = Field(None, gt=0)
    amenities: List[str] = Field(default_factory=list)
    contact: Optional[VenueContact] = None


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
    created_at: datetime = Field(default_factory=datetime.utcnow)

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
    radius_km: Optional[float] = Field(None, ge=0.1, le=1000)


class UserProfile(BaseModel):
    """User profile information"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    preferences: Optional[UserPreferences] = None


class UserBase(BaseModel):
    """Base user model"""
    email: str = Field(..., min_length=1, max_length=255)
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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


# Checkin Models
class CheckinBase(BaseModel):
    """Base checkin model"""
    event_id: PyObjectId
    user_id: PyObjectId
    qr_code: str = Field(..., min_length=1, max_length=100)
    ticket_tier: Optional[str] = Field(None, max_length=50)
    location: Optional[EventLocation] = None


class CheckinCreate(CheckinBase):
    """Model for creating checkins"""
    pass


class CheckinUpdate(BaseModel):
    """Model for updating checkins"""
    qr_code: Optional[str] = Field(None, min_length=1, max_length=100)
    ticket_tier: Optional[str] = Field(None, max_length=50)
    location: Optional[EventLocation] = None


class Checkin(CheckinBase):
    """Complete checkin model with database fields"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    check_in_time: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


# Query Models
class EventsNearbyQuery(BaseModel):
    """Query parameters for nearby events"""

    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    radius_km: float = Field(default=10, gt=0, le=100)
    limit: int = Field(default=50, gt=0, le=100)
