from datetime import datetime
from typing import Any, Optional

from bson import ObjectId

from .database import get_mongodb
from .models import Event, EventCreate, EventsNearbyQuery, EventUpdate


class EventService:
    """Service class for event operations"""

    def __init__(self):
        self.db = None

    def _ensure_db(self):
        """Ensure database connection is established"""
        if self.db is None:
            self.db = get_mongodb()
        return self.db

    def create_event(self, event_data: EventCreate) -> Event:
        """Create a new event"""
        db = self._ensure_db()
        event_dict = event_data.model_dump()
        event_dict["created_at"] = datetime.utcnow()
        event_dict["updated_at"] = datetime.utcnow()

        result = db.events.insert_one(event_dict)
        event_dict["_id"] = result.inserted_id

        return Event(**event_dict)

    def get_event(self, event_id: str) -> Optional[Event]:
        """Get event by ID"""
        if not ObjectId.is_valid(event_id):
            return None

        db = self._ensure_db()
        event_data = db.events.find_one({"_id": ObjectId(event_id)})
        if event_data:
            return Event(**event_data)
        return None

    def get_events(
        self,
        skip: int = 0,
        limit: int = 50,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[Event]:
        """Get events with pagination and filtering"""
        db = self._ensure_db()
        query = {}

        if category:
            query["category"] = category

        if search:
            query["$text"] = {"$search": search}

        cursor = db.events.find(query).skip(skip).limit(limit).sort("start_date", 1)
        return [Event(**event) for event in cursor]

    def update_event(self, event_id: str, event_data: EventUpdate) -> Optional[Event]:
        """Update an event"""
        if not ObjectId.is_valid(event_id):
            return None

        db = self._ensure_db()
        update_dict = {
            k: v
            for k, v in event_data.model_dump(exclude_unset=True).items()
            if v is not None
        }
        if not update_dict:
            return self.get_event(event_id)

        update_dict["updated_at"] = datetime.utcnow()

        result = db.events.update_one(
            {"_id": ObjectId(event_id)}, {"$set": update_dict}
        )

        if result.matched_count:
            return self.get_event(event_id)
        return None

    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        if not ObjectId.is_valid(event_id):
            return False

        db = self._ensure_db()
        result = db.events.delete_one({"_id": ObjectId(event_id)})
        return result.deleted_count > 0

    def get_events_nearby(self, query: EventsNearbyQuery) -> dict[str, Any]:
        """Get events near a location as GeoJSON"""
        db = self._ensure_db()
        pipeline = [
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [query.longitude, query.latitude],
                    },
                    "distanceField": "distance",
                    "maxDistance": query.radius_km * 1000,  # Convert to meters
                    "spherical": True,
                }
            },
            {"$limit": query.limit},
        ]

        events = list(db.events.aggregate(pipeline))

        # Convert to GeoJSON format
        features = []
        for event in events:
            feature = {
                "type": "Feature",
                "geometry": event["location"],
                "properties": {
                    "id": str(event["_id"]),
                    "title": event["title"],
                    "description": event.get("description", ""),
                    "category": event["category"],
                    "start_date": event["start_date"].isoformat(),
                    "organizer": event.get("organizer"),
                    "distance": round(event["distance"], 2),
                },
            }
            features.append(feature)

        return {"type": "FeatureCollection", "features": features}

    def get_categories(self) -> list[str]:
        """Get all unique categories"""
        db = self._ensure_db()
        return db.events.distinct("category")


# Global event service instance - lazy loaded
_event_service = None


def get_event_service():
    """Get event service instance (lazy loaded)"""
    global _event_service
    if _event_service is None:
        _event_service = EventService()
    return _event_service
