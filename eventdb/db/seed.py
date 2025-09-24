#!/usr/bin/env python3
"""
Generate sample data for the event database
"""
import os
import sys
from datetime import datetime, timedelta, timezone
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


def generate_events(venues, users, count=1000):
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
        if event["datetime"] < datetime.now(timezone.utc):
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


def generate_reviews(events, users, review_count=500):
    """Generate review data"""
    reviews = []
    
    # Review texts and titles
    review_texts = [
        "This event exceeded my expectations. The speakers were knowledgeable and engaging, and the networking opportunities were fantastic.",
        "Great event with excellent content. The venue was perfect and the organization was top-notch.",
        "I had a wonderful time at this event. The topics covered were relevant and the community was welcoming.",
        "The event was well-organized and the speakers were experts in their field. I learned a lot and met interesting people.",
        "This was one of the best events I've attended this year. Highly recommend to anyone interested in this topic.",
        "The event was okay, but I expected more interactive sessions. The content was good but could have been more engaging.",
        "Disappointing experience. The event didn't live up to the description and the venue was overcrowded.",
        "Good event overall, but the food was poor and the venue was too noisy. The content was valuable though.",
        "Excellent event with great speakers and well-organized activities. The networking was particularly valuable.",
        "The event was informative but the venue was too small for the number of attendees. Still worth attending."
    ]
    
    review_titles = [
        "Amazing experience!", "Great event overall", "Could be better", "Highly recommended",
        "Worth attending", "Disappointing", "Excellent organization", "Good value for money",
        "Well worth the time", "Not what I expected"
    ]
    
    review_tags = [
        "great-venue", "good-food", "excellent-speaker", "well-organized",
        "poor-venue", "bad-food", "disappointing", "disorganized",
        "crowded", "noisy", "expensive", "good-value", "family-friendly",
        "professional", "fun", "educational", "networking", "entertaining"
    ]
    
    for i in range(review_count):
        event = random.choice(events)
        user = random.choice(users)
        
        # Rating distribution: mostly positive (4-5 stars), some neutral (3), few negative (1-2)
        rating_weights = [0.05, 0.1, 0.15, 0.35, 0.35]  # 1, 2, 3, 4, 5 stars
        rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]
        
        # Select review text and title based on rating
        if rating >= 4:
            review_text = random.choice(review_texts[:5])  # Positive reviews
            title = random.choice(review_titles[:5])
        elif rating == 3:
            review_text = random.choice(review_texts[5:7])  # Neutral reviews
            title = random.choice(review_titles[5:7])
        else:
            review_text = random.choice(review_texts[7:])  # Negative reviews
            title = random.choice(review_titles[7:])
        
        # Generate tags based on rating
        num_tags = random.randint(1, 3)
        if rating >= 4:
            available_tags = [tag for tag in review_tags if tag in [
                "great-venue", "good-food", "excellent-speaker", "well-organized",
                "good-value", "family-friendly", "professional", "fun", 
                "educational", "networking", "entertaining"
            ]]
        elif rating == 3:
            available_tags = [tag for tag in review_tags if tag in [
                "professional", "educational", "networking"
            ]]
        else:
            available_tags = [tag for tag in review_tags if tag in [
                "poor-venue", "bad-food", "disappointing", "disorganized",
                "crowded", "noisy", "expensive"
            ]]
        
        selected_tags = random.sample(available_tags, min(num_tags, len(available_tags)))
        
        # Reviews are typically written after the event
        review_date = event["datetime"] + timedelta(days=random.randint(1, 30))
        
        review = {
            "event_id": event["_id"],
            "user_id": user["_id"],
            "rating": rating,
            "review_text": review_text,
            "title": title if random.random() < 0.7 else None,  # 70% have titles
            "helpful_votes": random.randint(0, 20) if random.random() < 0.3 else 0,
            "verified_attendee": random.random() < 0.8,  # 80% are verified
            "tags": selected_tags,
            "created_at": review_date,
            "updated_at": review_date if random.random() < 0.1 else None  # 10% have updates
        }
        reviews.append(review)
    
    return reviews


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
    db.reviews.drop()
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
    
    print("\nGenerating reviews...")
    reviews = generate_reviews(events, users, 500)
    result = db.reviews.insert_many(reviews)
    print(f"✓ Inserted {len(result.inserted_ids)} reviews")
    
    print("\n✅ Database seeded successfully!")
    
    # Display summary
    print("\nData Summary:")
    for collection_name in ["venues", "users", "events", "tickets", "checkins", "reviews"]:
        count = db[collection_name].count_documents({})
        print(f"  {collection_name}: {count} documents")


if __name__ == "__main__":
    seed_database()
