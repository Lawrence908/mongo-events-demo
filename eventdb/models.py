from datetime import datetime
from typing import Any, Optional, Literal
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator
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


class Location(BaseModel):
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


# User Models
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1, max_length=255)
    profile: Optional[dict] = None
    preferences: Optional[dict] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Venue Models
class VenueBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    location: Location
    address: str = Field(..., min_length=1, max_length=500)
    capacity: Optional[int] = Field(None, gt=0)


class VenueCreate(VenueBase):
    pass


class Venue(VenueBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Event Models
class EventBase(BaseModel):
    venueId: PyObjectId
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    tags: list[str] = Field(default_factory=list)
    datetime: datetime
    price: Optional[float] = Field(None, ge=0)
    seatsAvailable: int = Field(..., ge=0)


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[list[str]] = None
    datetime: Optional[datetime] = None
    price: Optional[float] = Field(None, ge=0)
    seatsAvailable: Optional[int] = Field(None, ge=0)


class Event(EventBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Ticket Models
class TicketBase(BaseModel):
    eventId: PyObjectId
    userId: PyObjectId
    pricePaid: float = Field(..., ge=0)
    status: Literal["active", "cancelled", "used"] = "active"


class TicketCreate(TicketBase):
    pass


class Ticket(TicketBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    purchasedAt: datetime = Field(default_factory=datetime.utcnow)


# Checkin Models
class CheckinBase(BaseModel):
    eventId: PyObjectId
    userId: PyObjectId
    location: Optional[Location] = None


class CheckinCreate(CheckinBase):
    pass


class Checkin(CheckinBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    at: datetime = Field(default_factory=datetime.utcnow)


# Query Models
class EventsNearbyQuery(BaseModel):
    lng: float = Field(..., ge=-180, le=180)
    lat: float = Field(..., ge=-90, le=90)
    km: float = Field(default=5, gt=0, le=20000)
    limit: int = Field(default=50, gt=0, le=100)


class TextSearchQuery(BaseModel):
    q: str = Field(..., min_length=1)
    limit: int = Field(default=50, gt=0, le=100)
