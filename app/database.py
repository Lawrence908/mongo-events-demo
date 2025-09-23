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
            self.events.create_index([("start_date", 1)], name="start_date")
            self.events.create_index([("created_at", 1)], name="created_at")
            self.events.create_index([("category", 1), ("start_date", 1)], name="category_start_date")
            self.events.create_index([("organizer", 1), ("start_date", 1)], name="organizer_start_date")
            self.events.create_index([("_id", 1), ("start_date", 1)], name="id_start_date")
            self.events.create_index([("category", 1), ("created_at", 1)], name="category_created_at")
            self.events.create_index([("start_date", 1), ("category", 1)], name="start_date_category")
            self.events.create_index([("tags", 1)], name="tags")
            self.events.create_index([("max_attendees", 1)], name="max_attendees")
            self.events.create_index([("end_date", 1)], name="end_date")
            print("✓ Event indexes created")

            # Venues indexes
            self.venues.create_index([("location", GEOSPHERE)], name="venue_location_2dsphere")
            self.venues.create_index([("name", 1)], name="venue_name")
            self.venues.create_index([("address.city", 1)], name="venue_city")
            self.venues.create_index([("created_at", 1)], name="venue_created_at")
            print("✓ Venue indexes created")

            # Users indexes
            self.users.create_index([("email", 1)], name="user_email", unique=True)
            self.users.create_index([("profile.first_name", 1), ("profile.last_name", 1)], name="user_name")
            self.users.create_index([("created_at", 1)], name="user_created_at")
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
            self.checkins.create_index([("event_id", 1)], name="event_id")
            self.checkins.create_index([("user_id", 1)], name="user_id")
            self.checkins.create_index([("venue_id", 1)], name="venue_id")
            print("✓ Basic reference indexes created")
            
            # 2. Time-based indexes for analytics
            self.checkins.create_index([("check_in_time", 1)], name="check_in_time")
            self.checkins.create_index([("created_at", 1)], name="created_at")
            print("✓ Time-based indexes created")
            
            # 3. Unique constraint for duplicate prevention (event_id + user_id)
            self.checkins.create_index([("event_id", 1), ("user_id", 1)], name="event_user_unique", unique=True)
            print("✓ Unique constraint index created")
            
            # 4. Analytics compound indexes
            self.checkins.create_index([("venue_id", 1), ("check_in_time", 1)], name="venue_time_analytics")
            self.checkins.create_index([("user_id", 1), ("check_in_time", 1)], name="user_time_analytics")
            self.checkins.create_index([("event_id", 1), ("check_in_time", 1)], name="event_time_analytics")
            print("✓ Analytics compound indexes created")
            
            # 5. Check-in method and ticket tier indexes
            self.checkins.create_index([("check_in_method", 1)], name="check_in_method")
            self.checkins.create_index([("ticket_tier", 1)], name="ticket_tier")
            print("✓ Check-in method and ticket tier indexes created")
            
            # 6. QR code index for lookups
            self.checkins.create_index([("qr_code", 1)], name="qr_code")
            print("✓ QR code index created")
            
            # 7. Metadata indexes for analytics
            self.checkins.create_index([("metadata.staff_verified", 1)], name="staff_verified")
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
            self.reviews.create_index([("event_id", 1)], name="event_id")
            self.reviews.create_index([("venue_id", 1)], name="venue_id")
            self.reviews.create_index([("user_id", 1)], name="user_id")
            print("✓ Basic reference indexes created")
            
            # 2. Time-based indexes for sorting and analytics
            self.reviews.create_index([("created_at", 1)], name="created_at")
            self.reviews.create_index([("updated_at", 1)], name="updated_at")
            print("✓ Time-based indexes created")
            
            # 3. Rating-based indexes for analytics
            self.reviews.create_index([("rating", 1)], name="rating")
            print("✓ Rating index created")
            
            # 4. Compound indexes for common query patterns
            self.reviews.create_index([("event_id", 1), ("created_at", -1)], name="event_created_desc")
            self.reviews.create_index([("venue_id", 1), ("created_at", -1)], name="venue_created_desc")
            self.reviews.create_index([("user_id", 1), ("created_at", -1)], name="user_created_desc")
            print("✓ Compound indexes created")
            
            # 5. Rating analytics indexes
            self.reviews.create_index([("event_id", 1), ("rating", 1)], name="event_rating")
            self.reviews.create_index([("venue_id", 1), ("rating", 1)], name="venue_rating")
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
