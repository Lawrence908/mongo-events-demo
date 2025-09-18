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

        # Apply schema validation to all collections
        self._apply_schema_validation()

        # Create comprehensive indexes for optimal query performance
        self._create_indexes()

        return self

    def _apply_schema_validation(self):
        """Apply JSON Schema validation to all collections"""
        schemas = get_all_schemas()
        
        # Apply schema validation to each collection
        for collection_name, schema in schemas.items():
            collection = getattr(self, collection_name)
            try:
                # Drop existing validation if any
                collection.drop()
                # Create collection with schema validation
                self.database.create_collection(collection_name, validator=schema)
                print(f"✓ Applied schema validation to {collection_name} collection")
            except Exception as e:
                print(f"Warning: Could not apply schema validation to {collection_name}: {e}")

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
            
            # 1. Geospatial index for location-based queries
            self.events.create_index([("location", GEOSPHERE)], name="location_2dsphere")
            print("✓ Geospatial index created")
            
            # 2. Text index for full-text search
            self.events.create_index(
                [
                    ("title", "text"),
                    ("description", "text"),
                    ("category", "text"),
                    ("tags", "text"),
                ],
                name="text_search"
            )
            print("✓ Text search index created")
            
            # 3. Date-based queries and sorting
            self.events.create_index([("start_date", 1)], name="start_date")
            self.events.create_index([("created_at", 1)], name="created_at")
            print("✓ Date-based indexes created")
            
            # 4. Compound indexes for common query patterns
            self.events.create_index([("category", 1), ("start_date", 1)], name="category_start_date")
            # Note: location_start_date compound index commented out to avoid conflict with location_2dsphere
            # self.events.create_index([("location", GEOSPHERE), ("start_date", 1)], name="location_start_date")
            self.events.create_index([("organizer", 1), ("start_date", 1)], name="organizer_start_date")
            print("✓ Compound indexes created")
            
            # 5. Cursor-based pagination support
            self.events.create_index([("_id", 1), ("start_date", 1)], name="id_start_date")
            print("✓ Pagination index created")
            
            # 6. Analytics and aggregation support
            self.events.create_index([("category", 1), ("created_at", 1)], name="category_created_at")
            self.events.create_index([("start_date", 1), ("category", 1)], name="start_date_category")
            print("✓ Analytics indexes created")
            
            # 7. Tags array queries
            self.events.create_index([("tags", 1)], name="tags")
            print("✓ Tags index created")
            
            # 8. Event status and filtering
            self.events.create_index([("max_attendees", 1)], name="max_attendees")
            self.events.create_index([("end_date", 1)], name="end_date")
            print("✓ Filtering indexes created")
            
            print("✓ All indexes created successfully")
            
        except Exception as e:
            print(f"Warning: Error creating indexes: {e}")
            # Don't raise the exception as indexes might already exist
            # MongoDB create_index is idempotent, but we want to be extra safe


# Global MongoDB instance
mongodb = MongoDB()


def get_mongodb() -> MongoDB:
    """Get MongoDB instance"""
    if not mongodb.is_connected():
        mongodb.connect()
    return mongodb
