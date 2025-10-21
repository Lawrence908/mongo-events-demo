import os
from typing import Optional

from dotenv import load_dotenv
from pymongo import GEOSPHERE, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from .schema_validation import get_all_schemas

load_dotenv()


class MongoDB:
    """MongoDB connection manager"""

    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.events: Optional[Collection] = None
        self.venues: Optional[Collection] = None
        self.users: Optional[Collection] = None
        self.checkins: Optional[Collection] = None
        self.reviews: Optional[Collection] = None

    def connect(self):
        """Connect to MongoDB and apply schema validation"""
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        db_name = os.getenv("MONGODB_DB_NAME", "events_demo")

        self.client = MongoClient(uri)
        self.database = self.client[db_name]
        self.events = self.database.events
        self.venues = self.database.venues
        self.users = self.database.users
        self.checkins = self.database.checkins
        self.reviews = self.database.reviews

        # Apply schema validation to all collections
        self._apply_schema_validation()

        # Create comprehensive indexes for optimal query performance
        self._create_indexes()

        return self

    def _apply_schema_validation(self):
        """Apply JSON Schema validation to all collections without data loss.

        Uses collMod when the collection already exists, otherwise creates the
        collection with the validator attached. Validation level is set to
        'moderate' so existing documents are not rejected but all new/updated
        documents must satisfy the schema.
        """
        schemas = get_all_schemas()

        for collection_name, schema in schemas.items():
            try:
                # Attempt to modify validator on existing collection
                self.database.command({
                    "collMod": collection_name,
                    "validator": schema,
                    "validationLevel": "moderate",
                })
                print(f"✓ Updated schema validation for {collection_name}")
            except Exception:
                # If collection does not exist yet, create it with the validator
                try:
                    self.database.create_collection(
                        collection_name,
                        validator=schema,
                        validationLevel="moderate",
                    )
                    print(f"✓ Created {collection_name} with schema validation")
                except Exception as e:
                    print(f"Warning: Could not apply schema for {collection_name}: {e}")

    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            self.events = None
            self.venues = None
            self.users = None
            self.checkins = None
            self.reviews = None

    def is_connected(self) -> bool:
        """Check if connected to MongoDB"""
        try:
            if self.client:
                self.client.admin.command("ping")
                return True
        except Exception:
            pass
        return False

    def list_indexes(self, collection_name: str = "events"):
        """List all indexes for a specific collection"""
        if not self.is_connected():
            raise Exception("Not connected to MongoDB")
        
        collection = getattr(self, collection_name, None)
        if collection is None:
            raise Exception(f"Collection '{collection_name}' not found")
        
        indexes = []
        for index in collection.list_indexes():
            indexes.append({
                'name': index['name'],
                'key': index.get('key', {}),
                'unique': index.get('unique', False),
                'sparse': index.get('sparse', False),
                'background': index.get('background', False),
                'textIndexVersion': index.get('textIndexVersion'),
                'weights': index.get('weights', {}),
                'default_language': index.get('default_language'),
                'language_override': index.get('language_override')
            })
        
        return indexes

    def _create_indexes(self):
        """Create all required indexes for optimal query performance"""
        try:
            print("Creating database indexes...")

            # Events indexes
            self.events.create_index([("location", GEOSPHERE)], name="location_2dsphere")
            self.events.create_index(
                [("title", "text"), ("description", "text"), ("category", "text"), ("tags", "text")],
                name="text_search",
            )
            self.events.create_index([("startDate", 1)], name="startDate")
            self.events.create_index([("createdAt", 1)], name="createdAt")
            self.events.create_index([("category", 1), ("startDate", 1)], name="category_startDate")
            self.events.create_index([("organizer", 1), ("startDate", 1)], name="organizer_startDate")
            self.events.create_index([("_id", 1), ("startDate", 1)], name="id_startDate")
            self.events.create_index([("category", 1), ("createdAt", 1)], name="category_createdAt")
            self.events.create_index([("startDate", 1), ("category", 1)], name="startDate_category")
            self.events.create_index([("tags", 1)], name="tags")
            self.events.create_index([("maxAttendees", 1)], name="maxAttendees")
            self.events.create_index([("endDate", 1)], name="endDate")
            print("✓ Event indexes created")

            # Venues indexes
            self.venues.create_index([("location", GEOSPHERE)], name="venue_location_2dsphere")
            self.venues.create_index([("name", 1)], name="venue_name")
            self.venues.create_index([("address.city", 1)], name="venue_city")
            self.venues.create_index([("createdAt", 1)], name="venue_createdAt")
            print("✓ Venue indexes created")

            # Users indexes
            self.users.create_index([("email", 1)], name="user_email", unique=True)
            self.users.create_index([("profile.firstName", 1), ("profile.lastName", 1)], name="user_name")
            self.users.create_index([("createdAt", 1)], name="user_createdAt")
            self.users.create_index([("profile.preferences.location", GEOSPHERE)], name="user_pref_location_2dsphere")
            print("✓ User indexes created")

            # Check-ins and Reviews dedicated index suites
            self._create_checkins_indexes()
            self._create_reviews_indexes()

            print("✓ All indexes created successfully")

        except Exception as e:
            print(f"Warning: Error creating indexes: {e}")

    def _create_checkins_indexes(self):
        """Create comprehensive indexes for check-ins collection"""
        try:
            print("Creating check-ins indexes...")
            
            # 1. Basic reference indexes
            self.checkins.create_index([("eventId", 1)], name="eventId")
            self.checkins.create_index([("userId", 1)], name="userId")
            self.checkins.create_index([("venueId", 1)], name="venueId")
            print("✓ Basic reference indexes created")
            
            # 2. Time-based indexes for analytics
            self.checkins.create_index([("checkInTime", 1)], name="checkInTime")
            self.checkins.create_index([("createdAt", 1)], name="createdAt")
            print("✓ Time-based indexes created")
            
            # 3. Unique constraint for duplicate prevention (event_id + user_id)
            self.checkins.create_index([("eventId", 1), ("userId", 1)], name="event_user_unique", unique=True)
            print("✓ Unique constraint index created")
            
            # 4. Analytics compound indexes
            self.checkins.create_index([("venueId", 1), ("checkInTime", 1)], name="venue_time_analytics")
            self.checkins.create_index([("userId", 1), ("checkInTime", 1)], name="user_time_analytics")
            self.checkins.create_index([("eventId", 1), ("checkInTime", 1)], name="event_time_analytics")
            print("✓ Analytics compound indexes created")
            
            # 5. Check-in method and ticket tier indexes
            self.checkins.create_index([("checkInMethod", 1)], name="checkInMethod")
            self.checkins.create_index([("ticketTier", 1)], name="ticketTier")
            print("✓ Check-in method and ticket tier indexes created")
            
            # 6. QR code index for lookups
            self.checkins.create_index([("qrCode", 1)], name="qrCode")
            print("✓ QR code index created")
            
            # 7. Metadata indexes for analytics
            self.checkins.create_index([("metadata.staffVerified", 1)], name="staffVerified")
            print("✓ Metadata indexes created")
            
            # 8. Geospatial index for check-in location (if different from event)
            self.checkins.create_index([("location", GEOSPHERE)], name="checkin_location_2dsphere")
            print("✓ Check-in location geospatial index created")
            
            print("✓ All check-ins indexes created successfully")
            
        except Exception as e:
            print(f"Warning: Error creating check-ins indexes: {e}")

    def _create_reviews_indexes(self):
        """Create comprehensive indexes for reviews collection"""
        try:
            print("Creating reviews indexes...")
            
            # 1. Basic reference indexes
            self.reviews.create_index([("eventId", 1)], name="eventId")
            self.reviews.create_index([("venueId", 1)], name="venueId")
            self.reviews.create_index([("userId", 1)], name="userId")
            print("✓ Basic reference indexes created")
            
            # 2. Time-based indexes for sorting and analytics
            self.reviews.create_index([("createdAt", 1)], name="createdAt")
            self.reviews.create_index([("updatedAt", 1)], name="updatedAt")
            print("✓ Time-based indexes created")
            
            # 3. Rating-based indexes for analytics
            self.reviews.create_index([("rating", 1)], name="rating")
            print("✓ Rating index created")
            
            # 4. Compound indexes for common query patterns
            self.reviews.create_index([("eventId", 1), ("createdAt", -1)], name="event_created_desc")
            self.reviews.create_index([("venueId", 1), ("createdAt", -1)], name="venue_created_desc")
            self.reviews.create_index([("userId", 1), ("createdAt", -1)], name="user_created_desc")
            print("✓ Compound indexes created")
            
            # 5. Rating analytics indexes
            self.reviews.create_index([("eventId", 1), ("rating", 1)], name="event_rating")
            self.reviews.create_index([("venueId", 1), ("rating", 1)], name="venue_rating")
            print("✓ Rating analytics indexes created")
            
            # 6. Text search index for comments
            self.reviews.create_index([("comment", "text")], name="comment_text")
            print("✓ Text search index created")
            
            print("✓ All reviews indexes created successfully")
            
        except Exception as e:
            print(f"Warning: Error creating reviews indexes: {e}")


# Global MongoDB instance
mongodb = MongoDB()


def get_mongodb() -> MongoDB:
    """Get MongoDB instance"""
    if not mongodb.is_connected():
        mongodb.connect()
    return mongodb
