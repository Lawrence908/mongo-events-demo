from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from bson import ObjectId

from .database import get_mongodb
from .models import (
    Event, EventCreate, EventsNearbyQuery, EventUpdate,
    Venue, VenueCreate, VenueUpdate,
    User, UserCreate, UserUpdate,
    Checkin, CheckinCreate, CheckinUpdate,
    Review, ReviewCreate, ReviewUpdate
)
from .utils import calculate_weekend_window
from .geocoding import get_geocoding_service, GeocodingError


class EventService:
    """Service class for event operations"""

    def __init__(self):
        self.db = None

    def _ensure_db(self):
        """Ensure database connection is established"""
        if self.db is None:
            self.db = get_mongodb()
        # Defensive: ensure collections are available
        if getattr(self.db, "events", None) is None:
            try:
                self.db.connect()
            except Exception:
                # Fallback to reconnect via accessor
                self.db = get_mongodb()
        return self.db

    def create_event(self, event_data: EventCreate) -> Event:
        """Create a new event with geocoding support"""
        db = self._ensure_db()
        event_dict = event_data.model_dump()
        
        # Handle geocoding if Google Maps API is configured
        try:
            geocoding_service = get_geocoding_service()
            event_dict = geocoding_service.validate_and_geocode_event(event_dict)
        except GeocodingError as e:
            # If geocoding fails, we can still create the event but log the error
            print(f"Warning: Geocoding failed for event creation: {str(e)}")
        except Exception as e:
            # If geocoding service is not available (no API key), continue without it
            print(f"Info: Geocoding service not available: {str(e)}")
        
        event_dict["createdAt"] = datetime.now(timezone.utc)
        event_dict["updatedAt"] = datetime.now(timezone.utc)

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
        projection = {}
        sort_criteria = []

        if category:
            query["category"] = category

        if search:
            query["$text"] = {"$search": search}
            # Add textScore projection for debugging
            projection["score"] = {"$meta": "textScore"}
            # Sort by textScore for relevance
            sort_criteria = [("score", {"$meta": "textScore"})]

        if upcoming_only:
            query["startDate"] = {"$gte": datetime.now(timezone.utc)}

        # Cursor-based pagination (preferred)
        if cursor_id is None or (cursor_id and ObjectId.is_valid(cursor_id)):
            # Add cursor condition if cursor_id is provided
            if cursor_id and ObjectId.is_valid(cursor_id):
                query["_id"] = {"$gt": ObjectId(cursor_id)}
            
            # Use textScore sorting if search is provided, otherwise use _id
            if not sort_criteria:
                sort_criteria = [("_id", 1)]
            
            cursor = db.events.find(query, projection).sort(sort_criteria).limit(limit)
            events = list(cursor)
            
            # Get next cursor
            next_cursor = str(events[-1]["_id"]) if events and len(events) == limit else None
            
            # Convert MongoDB documents to Event objects
            event_objects = []
            for event in events:
                # Ensure _id is properly mapped to id field
                if "_id" in event:
                    event["id"] = event["_id"]
                event_objects.append(Event(**event))
            
            return {
                "events": event_objects,
                "next_cursor": next_cursor,
                "has_more": len(events) == limit,
                "pagination_type": "cursor"
            }
        
        # Fallback to offset-based pagination for invalid cursor_id
        else:
            # Use textScore sorting if search is provided, otherwise use startDate
            if not sort_criteria:
                sort_criteria = [("startDate", 1)]
            
            cursor = db.events.find(query, projection).skip(skip).limit(limit).sort(sort_criteria)
            events = list(cursor)
            
            # Convert MongoDB documents to Event objects
            event_objects = []
            for event in events:
                # Ensure _id is properly mapped to id field
                if "_id" in event:
                    event["id"] = event["_id"]
                event_objects.append(Event(**event))
            
            return {
                "events": event_objects,
                "next_cursor": None,
                "has_more": len(events) == limit,
                "pagination_type": "offset",
                "offset": skip + len(events)
            }

    def update_event(self, event_id: str, event_data: EventUpdate) -> Optional[Event]:
        """Update an event with geocoding support"""
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

        # Handle geocoding if address or location is being updated
        if "address" in update_dict or "location" in update_dict:
            try:
                geocoding_service = get_geocoding_service()
                # Get current event data to merge with updates
                current_event = self.get_event(event_id)
                if current_event:
                    current_dict = current_event.model_dump()
                    current_dict.update(update_dict)
                    updated_dict = geocoding_service.validate_and_geocode_event(current_dict)
                    # Only update the fields that were actually changed
                    for key in ["location", "address", "directionsUrl"]:
                        if key in updated_dict:
                            update_dict[key] = updated_dict[key]
            except GeocodingError as e:
                print(f"Warning: Geocoding failed for event update: {str(e)}")
            except Exception as e:
                print(f"Info: Geocoding service not available: {str(e)}")

        update_dict["updatedAt"] = datetime.now(timezone.utc)

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

    def get_events_nearby(self, query: EventsNearbyQuery | dict, category: Optional[str] = None) -> dict[str, Any]:
        """Get events near a location as GeoJSON with optional category filtering"""
        db = self._ensure_db()

        # Allow passing a plain dict for backwards compatibility in some tests
        if isinstance(query, dict):
            query = EventsNearbyQuery(**query)
        pipeline = [
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [query.longitude, query.latitude],
                    },
                    "distanceField": "distance",
                    "maxDistance": query.radiusKm * 1000,  # Convert to meters
                    "spherical": True,
                    "key": "location"  # Specify which 2dsphere index to use
                }
            },
        ]
        
        # Add category filter if provided
        if category:
            pipeline.append({
                "$match": {
                    "category": category
                }
            })
        
        pipeline.append({"$limit": query.limit})

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
                    "startDate": event["startDate"].isoformat(),
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

    def get_events_this_weekend(self, longitude: float, latitude: float, radiusKm: float = 50, category: Optional[str] = None, limit: int = 50) -> dict[str, Any]:
        """Get events this weekend near a location with optional category filtering"""
        db = self._ensure_db()
        
        # Calculate weekend date range using the utility function
        friday, sunday = calculate_weekend_window()
        
        pipeline = [
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [longitude, latitude],
                    },
                    "distanceField": "distance",
                    "maxDistance": radiusKm * 1000,  # Convert to meters
                    "spherical": True,
                    "key": "location"  # Specify which 2dsphere index to use
                }
            },
            {
                "$match": {
                    "startDate": {
                        "$gte": friday,
                        "$lte": sunday
                    }
                }
            },
        ]
        
        # Add category filter if provided
        if category:
            pipeline[1]["$match"]["category"] = category
        
        pipeline.extend([
            {
                "$sort": {"startDate": 1}
            },
            {
                "$limit": limit
            }
        ])
        
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
                    "startDate": event["startDate"].isoformat(),
                    "endDate": event.get("endDate", "").isoformat() if event.get("endDate") else "",
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
            "totalEvents": len(features)
        }

    def get_analytics(self) -> dict[str, Any]:
        """Get comprehensive event analytics"""
        db = self._ensure_db()
        
        # Peak event times analysis
        peak_times_pipeline = [
            {
                "$group": {
                    "_id": {
                        "hour": {"$hour": "$startDate"},
                        "dayOfWeek": {"$dayOfWeek": "$startDate"}
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
                    "avg_attendees": {"$avg": "$maxAttendees"}
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
                        "year": {"$year": "$startDate"},
                        "month": {"$month": "$startDate"}
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
            "totalEvents": db.events.count_documents({}),
            "upcomingEvents": db.events.count_documents({"startDate": {"$gte": datetime.now(timezone.utc)}})
        }

    def get_events_by_date_range(
        self, 
        startDate: datetime, 
        endDate: datetime,
        category: Optional[str] = None,
        longitude: Optional[float] = None,
        latitude: Optional[float] = None,
        radiusKm: Optional[float] = None
    ) -> list[Event]:
        """Get events within a specific date range with optional location filtering"""
        db = self._ensure_db()
        query = {
            "startDate": {
                "$gte": startDate,
                "$lte": endDate
            }
        }
        
        if category:
            query["category"] = category
            
        if longitude and latitude and radiusKm:
            # Use geospatial query with date range
            pipeline = [
                {
                    "$geoNear": {
                        "near": {
                            "type": "Point",
                            "coordinates": [longitude, latitude],
                        },
                        "distanceField": "distance",
                        "maxDistance": radiusKm * 1000,
                        "spherical": True,
                    }
                },
                {
                    "$match": {
                        "startDate": {
                            "$gte": startDate,
                            "$lte": endDate
                        }
                    }
                },
                {
                    "$sort": {"startDate": 1}
                }
            ]
            
            if category:
                pipeline[1]["$match"]["category"] = category
                
            events = list(db.events.aggregate(pipeline))
            return [Event(**event) for event in events]
        else:
            # Regular date range query
            cursor = db.events.find(query).sort("startDate", 1)
            return [Event(**event) for event in cursor]


class VenueService:
    """Service class for venue operations"""

    def __init__(self):
        self.db = None

    def _ensure_db(self):
        """Ensure database connection is established"""
        if self.db is None:
            self.db = get_mongodb()
        return self.db

    def create_venue(self, venue_data: VenueCreate) -> Venue:
        """Create a new venue"""
        db = self._ensure_db()
        venue_dict = venue_data.model_dump()
        venue_dict["createdAt"] = datetime.now(timezone.utc)

        result = db.venues.insert_one(venue_dict)
        venue_dict["_id"] = result.inserted_id

        return Venue(**venue_dict)

    def get_venue(self, venue_id: str) -> Optional[Venue]:
        """Get venue by ID"""
        if not ObjectId.is_valid(venue_id):
            return None

        db = self._ensure_db()
        venue_data = db.venues.find_one({"_id": ObjectId(venue_id)})
        if venue_data:
            return Venue(**venue_data)
        return None

    def get_venues(self, skip: int = 0, limit: int = 50) -> dict[str, Any]:
        """Get venues with pagination"""
        db = self._ensure_db()
        cursor = db.venues.find().skip(skip).limit(limit).sort("createdAt", -1)
        venues = [Venue(**venue) for venue in cursor]

        return {
            "venues": venues,
            "has_more": len(venues) == limit,
            "offset": skip + len(venues)
        }

    def update_venue(self, venue_id: str, venue_data: VenueUpdate) -> Optional[Venue]:
        """Update a venue"""
        if not ObjectId.is_valid(venue_id):
            return None

        db = self._ensure_db()
        update_dict = {
            k: v
            for k, v in venue_data.model_dump(exclude_unset=True).items()
            if v is not None
        }
        if not update_dict:
            return self.get_venue(venue_id)

        result = db.venues.update_one(
            {"_id": ObjectId(venue_id)}, {"$set": update_dict}
        )

        if result.matched_count:
            return self.get_venue(venue_id)
        return None

    def delete_venue(self, venue_id: str) -> bool:
        """Delete a venue"""
        if not ObjectId.is_valid(venue_id):
            return False

        db = self._ensure_db()
        result = db.venues.delete_one({"_id": ObjectId(venue_id)})
        return result.deleted_count > 0


class UserService:
    """Service class for user operations"""

    def __init__(self):
        self.db = None

    def _ensure_db(self):
        """Ensure database connection is established"""
        if self.db is None:
            self.db = get_mongodb()
        return self.db

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        db = self._ensure_db()
        user_dict = user_data.model_dump()
        user_dict["createdAt"] = datetime.now(timezone.utc)

        result = db.users.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id

        return User(**user_dict)

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        if not ObjectId.is_valid(user_id):
            return None

        db = self._ensure_db()
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(**user_data)
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        db = self._ensure_db()
        user_data = db.users.find_one({"email": email})
        if user_data:
            return User(**user_data)
        return None

    def get_users(self, skip: int = 0, limit: int = 50) -> dict[str, Any]:
        """Get users with pagination"""
        db = self._ensure_db()
        cursor = db.users.find().skip(skip).limit(limit).sort("createdAt", -1)
        users = [User(**user) for user in cursor]

        return {
            "users": users,
            "has_more": len(users) == limit,
            "offset": skip + len(users)
        }

    def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update a user"""
        if not ObjectId.is_valid(user_id):
            return None

        db = self._ensure_db()
        update_dict = {
            k: v
            for k, v in user_data.model_dump(exclude_unset=True).items()
            if v is not None
        }
        if not update_dict:
            return self.get_user(user_id)

        result = db.users.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_dict}
        )

        if result.matched_count:
            return self.get_user(user_id)
        return None

    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        if not ObjectId.is_valid(user_id):
            return False

        db = self._ensure_db()
        result = db.users.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0


class CheckinService:
    """Service class for checkin operations with enhanced bridge table functionality"""

    def __init__(self):
        self.db = None

    def _ensure_db(self):
        """Ensure database connection is established"""
        if self.db is None:
            self.db = get_mongodb()
        return self.db

    def create_checkin(self, checkin_data: CheckinCreate) -> Checkin:
        """Create a new checkin with duplicate prevention"""
        db = self._ensure_db()
        checkin_dict = checkin_data.model_dump()
        checkin_dict["checkInTime"] = datetime.now(timezone.utc)
        checkin_dict["createdAt"] = datetime.now(timezone.utc)
        
        # Convert string IDs to ObjectId instances for MongoDB
        checkin_dict["eventId"] = ObjectId(checkin_dict["eventId"])
        checkin_dict["userId"] = ObjectId(checkin_dict["userId"])
        checkin_dict["venueId"] = ObjectId(checkin_dict["venueId"])

        # Check for duplicate check-in (event_id + user_id unique constraint)
        existing_checkin = db.checkins.find_one({
            "eventId": checkin_dict["eventId"],
            "userId": checkin_dict["userId"]
        })
        
        if existing_checkin:
            raise ValueError("User has already checked in to this event")

        result = db.checkins.insert_one(checkin_dict)
        checkin_dict["_id"] = result.inserted_id

        return Checkin(**checkin_dict)

    def get_checkin(self, checkin_id: str) -> Optional[Checkin]:
        """Get checkin by ID"""
        if not ObjectId.is_valid(checkin_id):
            return None

        db = self._ensure_db()
        checkin_data = db.checkins.find_one({"_id": ObjectId(checkin_id)})
        if checkin_data:
            return Checkin(**checkin_data)
        return None

    def get_checkin_by_event_user(self, event_id: str, user_id: str) -> Optional[Checkin]:
        """Get checkin by event and user (for duplicate checking)"""
        if not ObjectId.is_valid(event_id) or not ObjectId.is_valid(user_id):
            return None

        db = self._ensure_db()
        checkin_data = db.checkins.find_one({
            "eventId": ObjectId(event_id),
            "userId": ObjectId(user_id)
        })
        if checkin_data:
            return Checkin(**checkin_data)
        return None

    def get_checkins_by_event(self, event_id: str, skip: int = 0, limit: int = 50) -> dict[str, Any]:
        """Get checkins for a specific event"""
        if not ObjectId.is_valid(event_id):
            return {"checkins": [], "has_more": False, "offset": 0}

        db = self._ensure_db()
        cursor = db.checkins.find({"eventId": ObjectId(event_id)}).skip(skip).limit(limit).sort("checkInTime", -1)
        checkins = [Checkin(**checkin) for checkin in cursor]

        return {
            "checkins": checkins,
            "has_more": len(checkins) == limit,
            "offset": skip + len(checkins)
        }

    def get_checkins_by_user(self, user_id: str, skip: int = 0, limit: int = 50) -> dict[str, Any]:
        """Get checkins for a specific user"""
        if not ObjectId.is_valid(user_id):
            return {"checkins": [], "has_more": False, "offset": 0}

        db = self._ensure_db()
        cursor = db.checkins.find({"userId": ObjectId(user_id)}).skip(skip).limit(limit).sort("checkInTime", -1)
        checkins = [Checkin(**checkin) for checkin in cursor]

        return {
            "checkins": checkins,
            "has_more": len(checkins) == limit,
            "offset": skip + len(checkins)
        }

    def get_checkins_by_venue(self, venue_id: str, skip: int = 0, limit: int = 50) -> dict[str, Any]:
        """Get checkins for a specific venue (analytics)"""
        if not ObjectId.is_valid(venue_id):
            return {"checkins": [], "has_more": False, "offset": 0}

        db = self._ensure_db()
        cursor = db.checkins.find({"venueId": ObjectId(venue_id)}).skip(skip).limit(limit).sort("checkInTime", -1)
        checkins = [Checkin(**checkin) for checkin in cursor]

        return {
            "checkins": checkins,
            "has_more": len(checkins) == limit,
            "offset": skip + len(checkins)
        }

    def update_checkin(self, checkin_id: str, checkin_data: CheckinUpdate) -> Optional[Checkin]:
        """Update a checkin"""
        if not ObjectId.is_valid(checkin_id):
            return None

        db = self._ensure_db()
        update_dict = {
            k: v
            for k, v in checkin_data.model_dump(exclude_unset=True).items()
            if v is not None
        }
        if not update_dict:
            return self.get_checkin(checkin_id)

        result = db.checkins.update_one(
            {"_id": ObjectId(checkin_id)}, {"$set": update_dict}
        )

        if result.matched_count:
            return self.get_checkin(checkin_id)
        return None

    def delete_checkin(self, checkin_id: str) -> bool:
        """Delete a checkin"""
        if not ObjectId.is_valid(checkin_id):
            return False

        db = self._ensure_db()
        result = db.checkins.delete_one({"_id": ObjectId(checkin_id)})
        return result.deleted_count > 0

    # Analytics Methods
    def get_attendance_stats_by_event(self, event_id: str) -> dict[str, Any]:
        """Get attendance statistics for a specific event"""
        if not ObjectId.is_valid(event_id):
            return {"totalCheckins": 0, "uniqueUsers": 0, "checkinMethods": {}}

        db = self._ensure_db()
        
        pipeline = [
            {"$match": {"eventId": ObjectId(event_id)}},
            {
                "$group": {
                    "_id": None,
                    "totalCheckins": {"$sum": 1},
                    "uniqueUsers": {"$addToSet": "$userId"},
                    "checkinMethods": {"$push": "$checkInMethod"},
                    "avg_checkin_time": {"$avg": "$checkInTime"}
                }
            },
            {
                "$project": {
                    "totalCheckins": 1,
                    "uniqueUsers": {"$size": "$uniqueUsers"},
                    "checkinMethods": {
                        "$reduce": {
                            "input": "$checkinMethods",
                            "initialValue": {},
                            "in": {
                                "$mergeObjects": [
                                    "$$value",
                                    {
                                        "$arrayToObject": [
                                            [{"k": "$$this", "v": {"$add": [{"$ifNull": [{"$getField": {"field": "$$this", "input": "$$value"}}, 0]}, 1]}}]
                                        ]
                                    }
                                ]
                            }
                        }
                    },
                    "avg_checkin_time": 1
                }
            }
        ]
        
        result = list(db.checkins.aggregate(pipeline))
        if result:
            return result[0]
        return {"totalCheckins": 0, "uniqueUsers": 0, "checkinMethods": {}}

    def get_venue_attendance_stats(self, venue_id: str, startDate: Optional[datetime] = None, endDate: Optional[datetime] = None) -> dict[str, Any]:
        """Get attendance statistics for a specific venue"""
        if not ObjectId.is_valid(venue_id):
            return {"totalCheckins": 0, "uniqueUsers": 0, "eventsAttended": 0, "monthlyBreakdown": []}

        db = self._ensure_db()
        
        match_filter = {"venueId": ObjectId(venue_id)}
        if startDate:
            match_filter["checkInTime"] = {"$gte": startDate}
        if endDate:
            if "checkInTime" in match_filter:
                match_filter["checkInTime"]["$lte"] = endDate
            else:
                match_filter["checkInTime"] = {"$lte": endDate}

        pipeline = [
            {"$match": match_filter},
            {
                "$group": {
                    "_id": None,
                    "totalCheckins": {"$sum": 1},
                    "uniqueUsers": {"$addToSet": "$userId"},
                    "eventsAttended": {"$addToSet": "$eventId"},
                    "monthly_data": {
                        "$push": {
                            "month": {"$dateToString": {"format": "%Y-%m", "date": "$checkInTime"}},
                            "checkin_time": "$checkInTime"
                        }
                    }
                }
            },
            {
                "$project": {
                    "totalCheckins": 1,
                    "uniqueUsers": {"$size": "$uniqueUsers"},
                    "eventsAttended": {"$size": "$eventsAttended"},
                    "monthlyBreakdown": {
                        "$reduce": {
                            "input": "$monthly_data",
                            "initialValue": {},
                            "in": {
                                "$mergeObjects": [
                                    "$$value",
                                    {
                                        "$arrayToObject": [
                                            [{"k": "$$this.month", "v": {"$add": [{"$ifNull": [{"$getField": {"field": "$$this.month", "input": "$$value"}}, 0]}, 1]}}]
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        ]
        
        result = list(db.checkins.aggregate(pipeline))
        if result:
            return result[0]
        return {"totalCheckins": 0, "uniqueUsers": 0, "eventsAttended": 0, "monthlyBreakdown": []}

    def get_repeat_attendees(self, min_events: int = 2) -> list[dict[str, Any]]:
        """Get users who have attended multiple events (repeat attendees)"""
        db = self._ensure_db()
        
        pipeline = [
            {
                "$group": {
                    "_id": "$userId",
                    "event_count": {"$sum": 1},
                    "events": {"$addToSet": "$eventId"},
                    "venues": {"$addToSet": "$venueId"},
                    "first_checkin": {"$min": "$checkInTime"},
                    "last_checkin": {"$max": "$checkInTime"}
                }
            },
            {"$match": {"event_count": {"$gte": min_events}}},
            {"$sort": {"event_count": -1}},
            {
                "$project": {
                    "userId": "$_id",
                    "eventCount": 1,
                    "eventsAttended": {"$size": "$events"},
                    "venuesVisited": {"$size": "$venues"},
                    "firstCheckin": 1,
                    "lastCheckin": 1,
                    "events": 1,
                    "venues": 1
                }
            }
        ]
        
        return list(db.checkins.aggregate(pipeline))

    def get_checkin_time_patterns(self, venue_id: Optional[str] = None) -> dict[str, Any]:
        """Get check-in time patterns (peak hours, days of week)"""
        db = self._ensure_db()
        
        match_filter = {}
        if venue_id and ObjectId.is_valid(venue_id):
            match_filter["venueId"] = ObjectId(venue_id)
        
        pipeline = [
            {"$match": match_filter},
            {
                "$group": {
                    "_id": {
                        "hour": {"$hour": "$checkInTime"},
                        "dayOfWeek": {"$dayOfWeek": "$checkInTime"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {
                "$project": {
                    "hour": "$_id.hour",
                    "day_of_week": "$_id.dayOfWeek",
                    "checkin_count": "$count"
                }
            }
        ]
        
        result = list(db.checkins.aggregate(pipeline))
        return {
            "peak_hours": [r for r in result[:10]],  # Top 10 peak times
            "total_patterns": len(result)
        }

    def get_user_attendance_history(self, user_id: str, limit: int = 50) -> dict[str, Any]:
        """Get detailed attendance history for a user"""
        if not ObjectId.is_valid(user_id):
            return {"checkins": [], "summary": {}}

        db = self._ensure_db()
        
        # Get check-ins with event and venue details
        pipeline = [
            {"$match": {"userId": ObjectId(user_id)}},
            {
                "$lookup": {
                    "from": "events",
                    "localField": "eventId",
                    "foreignField": "_id",
                    "as": "event"
                }
            },
            {
                "$lookup": {
                    "from": "venues",
                    "localField": "venueId",
                    "foreignField": "_id",
                    "as": "venue"
                }
            },
            {"$unwind": "$event"},
            {"$unwind": "$venue"},
            {"$sort": {"checkInTime": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 1,
                    "eventId": 1,
                    "venueId": 1,
                    "checkInTime": 1,
                    "checkInMethod": 1,
                    "ticketTier": 1,
                    "event_title": "$event.title",
                    "event_category": "$event.category",
                    "venue_name": "$venue.name",
                    "venue_city": "$venue.address.city"
                }
            }
        ]
        
        checkins = list(db.checkins.aggregate(pipeline))
        
        # Get summary statistics
        summary_pipeline = [
            {"$match": {"userId": ObjectId(user_id)}},
            {
                "$group": {
                    "_id": None,
                    "totalEvents": {"$sum": 1},
                    "uniqueVenues": {"$addToSet": "$venueId"},
                    "categories": {"$addToSet": "$event.category"},
                    "firstCheckin": {"$min": "$checkInTime"},
                    "lastCheckin": {"$max": "$checkInTime"}
                }
            },
            {
                "$project": {
                    "totalEvents": 1,
                    "uniqueVenues": {"$size": "$uniqueVenues"},
                    "categoriesAttended": {"$size": "$categories"},
                    "firstCheckin": 1,
                    "lastCheckin": 1
                }
            }
        ]
        
        summary_result = list(db.checkins.aggregate(summary_pipeline))
        summary = summary_result[0] if summary_result else {}
        
        return {
            "checkins": checkins,
            "summary": summary
        }


class ReviewService:
    """Service class for review operations"""

    def __init__(self):
        self.db = None

    def _ensure_db(self):
        """Ensure database connection is established"""
        if self.db is None:
            self.db = get_mongodb()
        return self.db

    def create_review(self, review_data: ReviewCreate) -> Review:
        """Create a new review"""
        db = self._ensure_db()
        review_dict = review_data.model_dump()
        review_dict["createdAt"] = datetime.now(timezone.utc)
        review_dict["updatedAt"] = datetime.now(timezone.utc)

        # Convert string IDs to ObjectId instances for MongoDB
        if review_dict.get("eventId"):
            review_dict["eventId"] = ObjectId(review_dict["eventId"])
        if review_dict.get("venueId"):
            review_dict["venueId"] = ObjectId(review_dict["venueId"])
        review_dict["userId"] = ObjectId(review_dict["userId"])

        result = db.reviews.insert_one(review_dict)
        review_dict["_id"] = result.inserted_id

        return Review(**review_dict)

    def get_review(self, review_id: str) -> Optional[Review]:
        """Get review by ID"""
        if not ObjectId.is_valid(review_id):
            return None

        db = self._ensure_db()
        review_data = db.reviews.find_one({"_id": ObjectId(review_id)})
        if review_data:
            return Review(**review_data)
        return None

    def get_reviews_by_event(self, event_id: str, skip: int = 0, limit: int = 50) -> dict[str, Any]:
        """Get reviews for a specific event with pagination"""
        if not ObjectId.is_valid(event_id):
            return {"reviews": [], "has_more": False, "offset": 0}

        db = self._ensure_db()
        cursor = db.reviews.find({"eventId": ObjectId(event_id)}).skip(skip).limit(limit).sort("createdAt", -1)
        reviews = [Review(**review) for review in cursor]

        return {
            "reviews": reviews,
            "has_more": len(reviews) == limit,
            "offset": skip + len(reviews)
        }

    def get_reviews_by_venue(self, venue_id: str, skip: int = 0, limit: int = 50) -> dict[str, Any]:
        """Get reviews for a specific venue with pagination"""
        if not ObjectId.is_valid(venue_id):
            return {"reviews": [], "has_more": False, "offset": 0}

        db = self._ensure_db()
        cursor = db.reviews.find({"venueId": ObjectId(venue_id)}).skip(skip).limit(limit).sort("createdAt", -1)
        reviews = [Review(**review) for review in cursor]

        return {
            "reviews": reviews,
            "has_more": len(reviews) == limit,
            "offset": skip + len(reviews)
        }

    def get_reviews_by_user(self, user_id: str, skip: int = 0, limit: int = 50) -> dict[str, Any]:
        """Get reviews by a specific user with pagination"""
        if not ObjectId.is_valid(user_id):
            return {"reviews": [], "has_more": False, "offset": 0}

        db = self._ensure_db()
        cursor = db.reviews.find({"userId": ObjectId(user_id)}).skip(skip).limit(limit).sort("createdAt", -1)
        reviews = [Review(**review) for review in cursor]

        return {
            "reviews": reviews,
            "has_more": len(reviews) == limit,
            "offset": skip + len(reviews)
        }

    def update_review(self, review_id: str, review_data: ReviewUpdate) -> Optional[Review]:
        """Update a review"""
        if not ObjectId.is_valid(review_id):
            return None

        db = self._ensure_db()
        update_dict = {
            k: v
            for k, v in review_data.model_dump(exclude_unset=True).items()
            if v is not None
        }
        if not update_dict:
            return self.get_review(review_id)

        update_dict["updatedAt"] = datetime.now(timezone.utc)

        result = db.reviews.update_one(
            {"_id": ObjectId(review_id)}, {"$set": update_dict}
        )

        if result.matched_count:
            return self.get_review(review_id)
        return None

    def delete_review(self, review_id: str) -> bool:
        """Delete a review"""
        if not ObjectId.is_valid(review_id):
            return False

        db = self._ensure_db()
        result = db.reviews.delete_one({"_id": ObjectId(review_id)})
        return result.deleted_count > 0

    def get_review_stats_by_event(self, event_id: str) -> dict[str, Any]:
        """Get review statistics for a specific event"""
        if not ObjectId.is_valid(event_id):
            return {"totalReviews": 0, "averageRating": 0, "ratingDistribution": {}}

        db = self._ensure_db()
        
        pipeline = [
            {"$match": {"eventId": ObjectId(event_id)}},
            {
                "$group": {
                    "_id": None,
                    "totalReviews": {"$sum": 1},
                    "averageRating": {"$avg": "$rating"},
                    "rating_counts": {"$push": "$rating"}
                }
            },
            {
                "$project": {
                    "total_reviews": 1,
                    "averageRating": {"$round": ["$averageRating", 2]},
                    "ratingDistribution": {
                        "$reduce": {
                            "input": "$rating_counts",
                            "initialValue": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                            "in": {
                                "$mergeObjects": [
                                    "$$value",
                                    {
                                        "$arrayToObject": [
                                            [{"k": {"$toString": "$$this"}, "v": {"$add": [{"$ifNull": [{"$getField": {"field": {"$toString": "$$this"}, "input": "$$value"}}, 0]}, 1]}}]
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        ]
        
        result = list(db.reviews.aggregate(pipeline))
        if result:
            return result[0]
        return {"totalReviews": 0, "averageRating": 0, "ratingDistribution": {}}

    def get_review_stats_by_venue(self, venue_id: str) -> dict[str, Any]:
        """Get review statistics for a specific venue"""
        if not ObjectId.is_valid(venue_id):
            return {"totalReviews": 0, "averageRating": 0, "ratingDistribution": {}}

        db = self._ensure_db()
        
        pipeline = [
            {"$match": {"venueId": ObjectId(venue_id)}},
            {
                "$group": {
                    "_id": None,
                    "totalReviews": {"$sum": 1},
                    "averageRating": {"$avg": "$rating"},
                    "rating_counts": {"$push": "$rating"}
                }
            },
            {
                "$project": {
                    "total_reviews": 1,
                    "averageRating": {"$round": ["$averageRating", 2]},
                    "ratingDistribution": {
                        "$reduce": {
                            "input": "$rating_counts",
                            "initialValue": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                            "in": {
                                "$mergeObjects": [
                                    "$$value",
                                    {
                                        "$arrayToObject": [
                                            [{"k": {"$toString": "$$this"}, "v": {"$add": [{"$ifNull": [{"$getField": {"field": {"$toString": "$$this"}, "input": "$$value"}}, 0]}, 1]}}]
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        ]
        
        result = list(db.reviews.aggregate(pipeline))
        if result:
            return result[0]
        return {"totalReviews": 0, "averageRating": 0, "ratingDistribution": {}}

    def search_reviews(self, query: str, skip: int = 0, limit: int = 50) -> dict[str, Any]:
        """Search reviews by comment text"""
        db = self._ensure_db()
        
        # Use text search on comments
        search_query = {"$text": {"$search": query}}
        projection = {"score": {"$meta": "textScore"}}
        sort_criteria = [("score", {"$meta": "textScore"})]
        
        cursor = db.reviews.find(search_query, projection).sort(sort_criteria).skip(skip).limit(limit)
        reviews = [Review(**review) for review in cursor]

        return {
            "reviews": reviews,
            "has_more": len(reviews) == limit,
            "offset": skip + len(reviews)
        }


# Global service instances - lazy loaded
_event_service = None
_venue_service = None
_user_service = None
_checkin_service = None
_review_service = None


def get_event_service():
    """Get event service instance (lazy loaded)"""
    global _event_service
    if _event_service is None:
        _event_service = EventService()
    return _event_service


def get_venue_service():
    """Get venue service instance (lazy loaded)"""
    global _venue_service
    if _venue_service is None:
        _venue_service = VenueService()
    return _venue_service


def get_user_service():
    """Get user service instance (lazy loaded)"""
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service


def get_checkin_service():
    """Get checkin service instance (lazy loaded)"""
    global _checkin_service
    if _checkin_service is None:
        _checkin_service = CheckinService()
    return _checkin_service


def get_review_service():
    """Get review service instance (lazy loaded)"""
    global _review_service
    if _review_service is None:
        _review_service = ReviewService()
    return _review_service
