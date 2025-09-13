#!/usr/bin/env python3
"""
Generate sample data for the event database
"""
import os
import sys
from datetime import datetime, timedelta
from faker import Faker
from pymongo import MongoClient
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

fake = Faker()


def generate_venues(count=50):
    """Generate venue data with realistic coordinates"""
    venues = []
    
    # Major cities with realistic coordinates
    cities = [
        {"name": "New York", "lat": 40.7128, "lng": -74.0060},
        {"name": "Los Angeles", "lat": 34.0522, "lng": -118.2437},
        {"name": "Chicago", "lat": 41.8781, "lng": -87.6298},
        {"name": "Houston", "lat": 29.7604, "lng": -87.6298},
        {"name": "Phoenix", "lat": 33.4484, "lng": -112.0740},
        {"name": "Philadelphia", "lat": 39.9526, "lng": -75.1652},
        {"name": "San Antonio", "lat": 29.4241, "lng": -98.4936},
        {"name": "San Diego", "lat": 32.7157, "lng": -117.1611},
        {"name": "Dallas", "lat": 32.7767, "lng": -96.7970},
        {"name": "San Jose", "lat": 37.3382, "lng": -121.8863},
    ]
    
    for i in range(count):
        city = random.choice(cities)
        # Add some random variation to coordinates
        lat = city["lat"] + random.uniform(-0.1, 0.1)
        lng = city["lng"] + random.uniform(-0.1, 0.1)
        
        venue = {
            "name": fake.company() + " " + random.choice(["Hall", "Center", "Theater", "Arena", "Convention Center", "Stadium"]),
            "location": {
                "type": "Point",
                "coordinates": [lng, lat]
            },
            "address": fake.street_address() + ", " + city["name"],
            "capacity": random.randint(50, 5000)
        }
        venues.append(venue)
    
    return venues


def generate_users(count=200):
    """Generate user data"""
    users = []
    
    for i in range(count):
        user = {
            "name": fake.name(),
            "email": fake.email(),
            "profile": {
                "age": random.randint(18, 80),
                "interests": random.sample([
                    "music", "sports", "technology", "art", "food", "travel",
                    "books", "movies", "fitness", "gaming", "photography"
                ], random.randint(1, 4))
            },
            "preferences": {
                "notifications": random.choice([True, False]),
                "newsletter": random.choice([True, False])
            }
        }
        users.append(user)
    
    return users


def generate_events(count=1000, venues, users):
    """Generate event data"""
    events = []
    
    event_types = [
        "Concert", "Conference", "Workshop", "Meetup", "Exhibition",
        "Festival", "Seminar", "Party", "Sports Event", "Theater Show",
        "Comedy Show", "Art Gallery", "Food Festival", "Tech Talk",
        "Networking Event", "Charity Event", "Book Launch", "Product Demo"
    ]
    
    for i in range(count):
        venue = random.choice(venues)
        start_date = fake.date_time_between(start_date="-30d", end_date="+90d")
        duration_hours = random.randint(1, 8)
        end_date = start_date + timedelta(hours=duration_hours)
        
        event = {
            "venueId": venue["_id"],
            "title": f"{random.choice(event_types)}: {fake.catch_phrase()}",
            "description": fake.text(max_nb_chars=500),
            "tags": random.sample([
                "music", "tech", "business", "art", "food", "sports",
                "education", "entertainment", "networking", "charity"
            ], random.randint(1, 3)),
            "datetime": start_date,
            "price": round(random.uniform(0, 200), 2) if random.random() > 0.3 else None,
            "seatsAvailable": random.randint(10, venue["capacity"])
        }
        events.append(event)
    
    return events


def generate_tickets(events, users, ticket_count=500):
    """Generate ticket data"""
    tickets = []
    
    for i in range(ticket_count):
        event = random.choice(events)
        user = random.choice(users)
        
        ticket = {
            "eventId": event["_id"],
            "userId": user["_id"],
            "pricePaid": event.get("price", 0) or 0,
            "status": random.choices(
                ["active", "cancelled", "used"],
                weights=[80, 10, 10]
            )[0]
        }
        tickets.append(ticket)
    
    return tickets


def generate_checkins(events, users, checkin_count=300):
    """Generate checkin data"""
    checkins = []
    
    for i in range(checkin_count):
        event = random.choice(events)
        user = random.choice(users)
        
        # Only generate checkins for past events
        if event["datetime"] < datetime.utcnow():
            checkin = {
                "eventId": event["_id"],
                "userId": user["_id"],
                "at": fake.date_time_between(
                    start_date=event["datetime"],
                    end_date=event["datetime"] + timedelta(hours=8)
                ),
                "location": event.get("location")  # Use event location if available
            }
            checkins.append(checkin)
    
    return checkins


def seed_database():
    """Main seeding function"""
    client = MongoClient(Config.MONGODB_URI)
    db = client[Config.DB_NAME]
    
    print(f"Seeding database: {Config.DB_NAME}")
    print(f"Using connection: {Config.MONGODB_URI}")
    
    # Clear existing data
    print("\nClearing existing data...")
    db.events.drop()
    db.venues.drop()
    db.users.drop()
    db.tickets.drop()
    db.checkins.drop()
    print("✓ Existing data cleared")
    
    # Generate and insert data
    print("\nGenerating venues...")
    venues = generate_venues(50)
    result = db.venues.insert_many(venues)
    print(f"✓ Inserted {len(result.inserted_ids)} venues")
    
    print("\nGenerating users...")
    users = generate_users(200)
    result = db.users.insert_many(users)
    print(f"✓ Inserted {len(result.inserted_ids)} users")
    
    print("\nGenerating events...")
    events = generate_events(1000, venues, users)
    result = db.events.insert_many(events)
    print(f"✓ Inserted {len(result.inserted_ids)} events")
    
    print("\nGenerating tickets...")
    tickets = generate_tickets(events, users, 500)
    result = db.tickets.insert_many(tickets)
    print(f"✓ Inserted {len(result.inserted_ids)} tickets")
    
    print("\nGenerating checkins...")
    checkins = generate_checkins(events, users, 300)
    result = db.checkins.insert_many(checkins)
    print(f"✓ Inserted {len(result.inserted_ids)} checkins")
    
    print("\n✅ Database seeded successfully!")
    
    # Display summary
    print("\nData Summary:")
    for collection_name in ["venues", "users", "events", "tickets", "checkins"]:
        count = db[collection_name].count_documents({})
        print(f"  {collection_name}: {count} documents")


if __name__ == "__main__":
    seed_database()
