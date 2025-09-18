#!/usr/bin/env python3
"""
Generate test data specifically for map visualization testing
Creates events with diverse categories and locations for EVE-14 testing
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import math

# Sample data for realistic event generation
CATEGORIES = [
    "Technology", "Music", "Sports", "Food & Drink", "Arts & Culture",
    "Business", "Education", "Health & Wellness", "Entertainment", "Community",
    "Science", "Fashion", "Travel", "Photography", "Gaming", "Networking"
]

# Major US cities with coordinates for diverse geographic distribution
CITIES = [
    {"name": "New York", "lat": 40.7128, "lng": -74.0060},
    {"name": "Los Angeles", "lat": 34.0522, "lng": -118.2437},
    {"name": "Chicago", "lat": 41.8781, "lng": -87.6298},
    {"name": "Houston", "lat": 29.7604, "lng": -95.3698},
    {"name": "Phoenix", "lat": 33.4484, "lng": -112.0740},
    {"name": "Philadelphia", "lat": 39.9526, "lng": -75.1652},
    {"name": "San Antonio", "lat": 29.4241, "lng": -98.4936},
    {"name": "San Diego", "lat": 32.7157, "lng": -117.1611},
    {"name": "Dallas", "lat": 32.7767, "lng": -96.7970},
    {"name": "San Jose", "lat": 37.3382, "lng": -121.8863},
    {"name": "Austin", "lat": 30.2672, "lng": -97.7431},
    {"name": "Jacksonville", "lat": 30.3322, "lng": -81.6557},
    {"name": "Fort Worth", "lat": 32.7555, "lng": -97.3308},
    {"name": "Columbus", "lat": 39.9612, "lng": -82.9988},
    {"name": "Charlotte", "lat": 35.2271, "lng": -80.8431},
    {"name": "San Francisco", "lat": 37.7749, "lng": -122.4194},
    {"name": "Indianapolis", "lat": 39.7684, "lng": -86.1581},
    {"name": "Seattle", "lat": 47.6062, "lng": -122.3321},
    {"name": "Denver", "lat": 39.7392, "lng": -104.9903},
    {"name": "Washington", "lat": 38.9072, "lng": -77.0369}
]

EVENT_TITLES = {
    "Technology": [
        "Tech Meetup", "AI Workshop", "Blockchain Conference", "DevOps Summit",
        "Machine Learning Bootcamp", "Cloud Computing Seminar", "Cybersecurity Talk",
        "Data Science Workshop", "Mobile App Development", "Web Development Course"
    ],
    "Music": [
        "Jazz Night", "Rock Concert", "Electronic Music Festival", "Classical Performance",
        "Indie Music Show", "Hip Hop Battle", "Acoustic Session", "Symphony Orchestra",
        "Folk Music Gathering", "Blues Jam Session"
    ],
    "Sports": [
        "Marathon Run", "Basketball Tournament", "Soccer Match", "Tennis Championship",
        "Swimming Competition", "Cycling Race", "Yoga Class", "CrossFit Challenge",
        "Boxing Training", "Volleyball League"
    ],
    "Food & Drink": [
        "Wine Tasting", "Cooking Class", "Food Festival", "Beer Brewing Workshop",
        "Coffee Cupping", "Cocktail Mixing", "Farmers Market", "Chef's Table",
        "Chocolate Making", "Sake Tasting"
    ],
    "Arts & Culture": [
        "Art Exhibition", "Museum Tour", "Theater Performance", "Poetry Reading",
        "Dance Workshop", "Film Screening", "Cultural Festival", "Book Club Meeting",
        "Photography Walk", "Pottery Class"
    ]
}

DESCRIPTIONS = [
    "Join us for an exciting event featuring industry experts and networking opportunities.",
    "A unique experience that brings together like-minded individuals from various backgrounds.",
    "Discover new trends and innovations in this dynamic field through interactive sessions.",
    "Connect with professionals and enthusiasts while learning something new.",
    "An immersive experience designed to inspire and educate participants.",
    "Come together to celebrate creativity, innovation, and community spirit.",
    "A hands-on workshop that combines learning with practical application.",
    "Experience the latest developments and connect with industry leaders.",
    "A collaborative event focused on sharing knowledge and building relationships.",
    "Join us for an engaging session that promises to be both informative and fun."
]

ORGANIZERS = [
    "Tech Innovators Inc.", "Creative Events Co.", "Community Hub", "Professional Network",
    "Local Business Association", "Educational Foundation", "Cultural Center",
    "Sports Club", "Art Collective", "Science Society", "Music Group", "Food Network"
]

def generate_random_coordinates(city: Dict[str, Any]) -> tuple[float, float]:
    """Generate random coordinates within a city area"""
    # Add random variation within ~10km radius
    lat_offset = random.uniform(-0.1, 0.1)
    lng_offset = random.uniform(-0.1, 0.1)
    
    return city["lng"] + lng_offset, city["lat"] + lat_offset

def generate_event_times() -> tuple[datetime, datetime]:
    """Generate realistic event start and end times"""
    # Events can be from 1 week ago to 3 months in the future
    days_offset = random.randint(-7, 90)
    start_date = datetime.now() + timedelta(days=days_offset)
    
    # Random time of day
    start_date = start_date.replace(
        hour=random.randint(8, 20),
        minute=random.choice([0, 15, 30, 45]),
        second=0,
        microsecond=0
    )
    
    # Duration between 1-8 hours
    duration_hours = random.randint(1, 8)
    end_date = start_date + timedelta(hours=duration_hours)
    
    return start_date, end_date

def generate_event() -> Dict[str, Any]:
    """Generate a single event with realistic data"""
    category = random.choice(CATEGORIES)
    city = random.choice(CITIES)
    lng, lat = generate_random_coordinates(city)
    start_date, end_date = generate_event_times()
    
    # Get appropriate title for category
    if category in EVENT_TITLES:
        title = random.choice(EVENT_TITLES[category])
    else:
        title = f"{category} Event"
    
    # Add some variation to titles
    if random.random() < 0.3:
        title += f" {random.randint(2024, 2025)}"
    
    event = {
        "title": title,
        "description": random.choice(DESCRIPTIONS),
        "category": category,
        "location": {
            "type": "Point",
            "coordinates": [lng, lat]
        },
        "start_date": start_date,
        "end_date": end_date,
        "organizer": random.choice(ORGANIZERS),
        "max_attendees": random.randint(10, 1000) if random.random() < 0.8 else None,
        "tags": [category.lower().replace(" ", "-"), "event", "local"],
        "created_at": start_date - timedelta(days=random.randint(1, 30)),
        "updated_at": start_date - timedelta(days=random.randint(1, 30))
    }
    
    return event

def generate_events(count: int = 100) -> List[Dict[str, Any]]:
    """Generate a list of events for map testing"""
    print(f"Generating {count} events for map testing...")
    events = []
    
    for i in range(count):
        if (i + 1) % 20 == 0:
            print(f"Generated {i + 1} events...")
        events.append(generate_event())
    
    return events

def save_to_json(events: List[Dict[str, Any]], filename: str = "map_test_events.json"):
    """Save events to JSON file"""
    # Convert datetime objects to ISO format strings
    for event in events:
        event["start_date"] = event["start_date"].isoformat()
        event["end_date"] = event["end_date"].isoformat()
        event["created_at"] = event["created_at"].isoformat()
        event["updated_at"] = event["updated_at"].isoformat()
    
    with open(filename, 'w') as f:
        json.dump(events, f, indent=2)
    
    print(f"Saved {len(events)} events to {filename}")

def main():
    """Generate test data for map visualization"""
    print("Generating test data for EVE-14 Map Page...")
    
    # Generate 100 events for testing
    events = generate_events(100)
    
    # Save to JSON file
    save_to_json(events)
    
    # Print summary
    print("\nEvent Summary:")
    category_counts = {}
    for event in events:
        category = event["category"]
        category_counts[category] = category_counts.get(category, 0) + 1
    
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count} events")
    
    print(f"\nTotal events generated: {len(events)}")
    print("Test data ready for map visualization testing!")

if __name__ == "__main__":
    main()
