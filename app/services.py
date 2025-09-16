from datetime import datetime, timedelta
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
        cursor_id: Optional[str] = None,
        upcoming_only: bool = True,
    ) -> dict[str, Any]:
        """Get events with pagination and filtering
        
        Args:
            skip: Offset for traditional pagination (fallback)
            limit: Number of events to return
            category: Filter by event category
            search: Text search query
            cursor_id: Cursor for pagination (preferred method)
            upcoming_only: Only return future events
            
        Returns:
            Dictionary with events, pagination info, and next cursor
        """
        db = self._ensure_db()
        query = {}

        if category:
            query["category"] = category

        if search:
            query["$text"] = {"$search": search}

        if upcoming_only:
            query["start_date"] = {"$gte": datetime.utcnow()}

        # Cursor-based pagination (preferred)
        if cursor_id and ObjectId.is_valid(cursor_id):
            query["_id"] = {"$gt": ObjectId(cursor_id)}
            cursor = db.events.find(query).sort("_id", 1).limit(limit)
            events = list(cursor)
            
            # Get next cursor
            next_cursor = str(events[-1]["_id"]) if events and len(events) == limit else None
            
            return {
                "events": [Event(**event) for event in events],
                "next_cursor": next_cursor,
                "has_more": len(events) == limit,
                "pagination_type": "cursor"
            }
        
        # Fallback to offset-based pagination
        else:
            cursor = db.events.find(query).skip(skip).limit(limit).sort("start_date", 1)
            events = [Event(**event) for event in cursor]
            
            return {
                "events": events,
                "next_cursor": None,
                "has_more": len(events) == limit,
                "pagination_type": "offset",
                "offset": skip + len(events)
            }

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

    def get_events_this_weekend(self, longitude: float, latitude: float, radius_km: float = 50) -> dict[str, Any]:
        """Get events this weekend near a location - perfect for your use case!"""
        db = self._ensure_db()
        
        # Calculate weekend date range
        now = datetime.utcnow()
        # Find this Friday
        days_until_friday = (4 - now.weekday()) % 7
        if days_until_friday == 0 and now.hour >= 18:  # If it's Friday evening, start from next Friday
            days_until_friday = 7
        friday = now.replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=days_until_friday)
        sunday = friday + timedelta(days=2, hours=23, minutes=59)
        
        pipeline = [
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [longitude, latitude],
                    },
                    "distanceField": "distance",
                    "maxDistance": radius_km * 1000,  # Convert to meters
                    "spherical": True,
                }
            },
            {
                "$match": {
                    "start_date": {
                        "$gte": friday,
                        "$lte": sunday
                    }
                }
            },
            {
                "$sort": {"start_date": 1}
            },
            {
                "$limit": 100
            }
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
                    "end_date": event.get("end_date", "").isoformat() if event.get("end_date") else "",
                    "organizer": event.get("organizer", ""),
                    "distance": round(event["distance"], 2),
                    "tags": event.get("tags", []),
                },
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection", 
            "features": features,
            "weekend_range": {
                "start": friday.isoformat(),
                "end": sunday.isoformat()
            },
            "total_events": len(features)
        }

    def get_analytics(self) -> dict[str, Any]:
        """Get comprehensive event analytics"""
        db = self._ensure_db()
        
        # Peak event times analysis
        peak_times_pipeline = [
            {
                "$group": {
                    "_id": {
                        "hour": {"$hour": "$start_date"},
                        "dayOfWeek": {"$dayOfWeek": "$start_date"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": 10
            }
        ]
        
        # Category popularity
        category_pipeline = [
            {
                "$group": {
                    "_id": "$category",
                    "count": {"$sum": 1},
                    "avg_attendees": {"$avg": "$max_attendees"}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ]
        
        # Monthly event trends
        monthly_trends_pipeline = [
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$start_date"},
                        "month": {"$month": "$start_date"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id.year": 1, "_id.month": 1}
            }
        ]
        
        peak_times = list(db.events.aggregate(peak_times_pipeline))
        category_stats = list(db.events.aggregate(category_pipeline))
        monthly_trends = list(db.events.aggregate(monthly_trends_pipeline))
        
        return {
            "peak_event_times": peak_times,
            "category_popularity": category_stats,
            "monthly_trends": monthly_trends,
            "total_events": db.events.count_documents({}),
            "upcoming_events": db.events.count_documents({"start_date": {"$gte": datetime.utcnow()}})
        }

    def get_events_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime,
        category: Optional[str] = None,
        longitude: Optional[float] = None,
        latitude: Optional[float] = None,
        radius_km: Optional[float] = None
    ) -> list[Event]:
        """Get events within a specific date range with optional location filtering"""
        db = self._ensure_db()
        query = {
            "start_date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        if category:
            query["category"] = category
            
        if longitude and latitude and radius_km:
            # Use geospatial query with date range
            pipeline = [
                {
                    "$geoNear": {
                        "near": {
                            "type": "Point",
                            "coordinates": [longitude, latitude],
                        },
                        "distanceField": "distance",
                        "maxDistance": radius_km * 1000,
                        "spherical": True,
                    }
                },
                {
                    "$match": {
                        "start_date": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                {
                    "$sort": {"start_date": 1}
                }
            ]
            
            if category:
                pipeline[1]["$match"]["category"] = category
                
            events = list(db.events.aggregate(pipeline))
            return [Event(**event) for event in events]
        else:
            # Regular date range query
            cursor = db.events.find(query).sort("start_date", 1)
            return [Event(**event) for event in cursor]


# Global event service instance - lazy loaded
_event_service = None


def get_event_service():
    """Get event service instance (lazy loaded)"""
    global _event_service
    if _event_service is None:
        _event_service = EventService()
    return _event_service
