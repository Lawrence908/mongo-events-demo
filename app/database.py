import os
from typing import Optional

from dotenv import load_dotenv
from pymongo import GEOSPHERE, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

load_dotenv()


class MongoDB:
    """MongoDB connection manager"""

    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.events: Optional[Collection] = None

    def connect(self):
        """Connect to MongoDB"""
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        db_name = os.getenv("MONGODB_DB_NAME", "events_demo")

        self.client = MongoClient(uri)
        self.database = self.client[db_name]
        self.events = self.database.events

        # Create comprehensive indexes for optimal query performance
        
        # 1. Geospatial index for location-based queries
        self.events.create_index([("location", GEOSPHERE)])
        
        # 2. Text index for full-text search
        self.events.create_index(
            [
                ("title", "text"),
                ("description", "text"),
                ("category", "text"),
                ("tags", "text"),
            ]
        )
        
        # 3. Date-based queries and sorting
        self.events.create_index([("start_date", 1)])
        self.events.create_index([("created_at", 1)])
        
        # 4. Compound indexes for common query patterns
        self.events.create_index([("category", 1), ("start_date", 1)])
        self.events.create_index([("location", GEOSPHERE), ("start_date", 1)])
        self.events.create_index([("organizer", 1), ("start_date", 1)])
        
        # 5. Cursor-based pagination support
        self.events.create_index([("_id", 1), ("start_date", 1)])
        
        # 6. Analytics and aggregation support
        self.events.create_index([("category", 1), ("created_at", 1)])
        self.events.create_index([("start_date", 1), ("category", 1)])
        
        # 7. Tags array queries
        self.events.create_index([("tags", 1)])
        
        # 8. Event status and filtering
        self.events.create_index([("max_attendees", 1)])
        self.events.create_index([("end_date", 1)])

        return self

    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            self.events = None

    def is_connected(self) -> bool:
        """Check if connected to MongoDB"""
        try:
            if self.client:
                self.client.admin.command("ping")
                return True
        except Exception:
            pass
        return False


# Global MongoDB instance
mongodb = MongoDB()


def get_mongodb() -> MongoDB:
    """Get MongoDB instance"""
    if not mongodb.is_connected():
        mongodb.connect()
    return mongodb
