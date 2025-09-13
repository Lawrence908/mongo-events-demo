#!/usr/bin/env python3
"""
Create all required indexes for the event database
"""
import os
import sys
from pymongo import MongoClient, TEXT, GEO2DSPHERE

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


def create_indexes():
    """Create all required indexes"""
    client = MongoClient(Config.MONGODB_URI)
    db = client[Config.DB_NAME]
    
    print(f"Creating indexes for database: {Config.DB_NAME}")
    print(f"Using connection: {Config.MONGODB_URI}")
    
    # Events collection indexes
    print("\nCreating events indexes...")
    
    # Text search index
    db.events.create_index([
        ("title", TEXT),
        ("description", TEXT),
        ("tags", TEXT)
    ], name="text_search")
    print("✓ Text search index created")
    
    # Compound index for venue and datetime queries
    db.events.create_index([
        ("venueId", 1),
        ("datetime", 1)
    ], name="venue_datetime")
    print("✓ Venue-datetime compound index created")
    
    # Venues collection indexes
    print("\nCreating venues indexes...")
    
    # Geospatial index for location queries
    db.venues.create_index([
        ("location", GEO2DSPHERE)
    ], name="location_geo")
    print("✓ Venue location geospatial index created")
    
    # Users collection indexes
    print("\nCreating users indexes...")
    
    # Unique email index
    db.users.create_index([
        ("email", 1)
    ], unique=True, name="email_unique")
    print("✓ User email unique index created")
    
    # Tickets collection indexes
    print("\nCreating tickets indexes...")
    
    # Compound index for event and user queries
    db.tickets.create_index([
        ("eventId", 1),
        ("userId", 1)
    ], name="event_user")
    print("✓ Ticket event-user compound index created")
    
    # Status index for filtering
    db.tickets.create_index([
        ("status", 1)
    ], name="status")
    print("✓ Ticket status index created")
    
    # Checkins collection indexes
    print("\nCreating checkins indexes...")
    
    # Event and user compound index
    db.checkins.create_index([
        ("eventId", 1),
        ("userId", 1)
    ], name="event_user")
    print("✓ Checkin event-user compound index created")
    
    # Timestamp index for time-based queries
    db.checkins.create_index([
        ("at", -1)
    ], name="timestamp")
    print("✓ Checkin timestamp index created")
    
    print("\n✅ All indexes created successfully!")
    
    # Display index information
    print("\nIndex Summary:")
    for collection_name in ["events", "venues", "users", "tickets", "checkins"]:
        collection = db[collection_name]
        indexes = list(collection.list_indexes())
        print(f"\n{collection_name}:")
        for index in indexes:
            print(f"  - {index['name']}: {index.get('key', {})}")


if __name__ == "__main__":
    create_indexes()
