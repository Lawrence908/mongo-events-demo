#!/usr/bin/env python3
"""
Test Data Generator for MongoDB Events Demo
Generates 10,000+ events with realistic geospatial data for testing
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
    "A unique experience that brings together like-minded individuals in a collaborative environment.",
    "Don't miss this exclusive event with hands-on activities and interactive sessions.",
    "An educational and entertaining event perfect for professionals and enthusiasts alike.",
    "Connect with peers, learn new skills, and enjoy great food and drinks.",
    "A community-driven event focused on sharing knowledge and building relationships.",
    "Experience something new and exciting in a welcoming and inclusive atmosphere.",
    "Perfect for beginners and experts looking to expand their horizons and network."
]

ORGANIZERS = [
    "TechCorp Events", "Local Community Center", "University Extension", "Creative Hub",
    "Sports Club", "Cultural Society", "Professional Association", "Startup Incubator",
    "Art Gallery", "Music Venue", "Conference Center", "Co-working Space"
]

TAGS = [
    "networking", "learning", "fun", "professional", "social", "educational",
    "interactive", "hands-on", "beginner-friendly", "expert-level", "free",
    "paid", "outdoor", "indoor", "virtual", "in-person", "family-friendly",
    "adults-only", "team-building", "creative", "technical", "artistic"
]

# Major cities with coordinates for realistic geospatial distribution
CITIES = [
    {"name": "New York", "lat": 40.7128, "lng": -74.0060, "radius": 50},
    {"name": "Los Angeles", "lat": 34.0522, "lng": -118.2437, "radius": 60},
    {"name": "Chicago", "lat": 41.8781, "lng": -87.6298, "radius": 40},
    {"name": "Houston", "lat": 29.7604, "lng": -95.3698, "radius": 45},
    {"name": "Phoenix", "lat": 33.4484, "lng": -112.0740, "radius": 35},
    {"name": "Philadelphia", "lat": 39.9526, "lng": -75.1652, "radius": 30},
    {"name": "San Antonio", "lat": 29.4241, "lng": -98.4936, "radius": 25},
    {"name": "San Diego", "lat": 32.7157, "lng": -117.1611, "radius": 30},
    {"name": "Dallas", "lat": 32.7767, "lng": -96.7970, "radius": 35},
    {"name": "San Jose", "lat": 37.3382, "lng": -121.8863, "radius": 25},
    {"name": "Austin", "lat": 30.2672, "lng": -97.7431, "radius": 30},
    {"name": "Jacksonville", "lat": 30.3322, "lng": -81.6557, "radius": 40},
    {"name": "Fort Worth", "lat": 32.7555, "lng": -97.3308, "radius": 25},
    {"name": "Columbus", "lat": 39.9612, "lng": -82.9988, "radius": 30},
    {"name": "Charlotte", "lat": 35.2271, "lng": -80.8431, "radius": 25},
    {"name": "San Francisco", "lat": 37.7749, "lng": -122.4194, "radius": 20},
    {"name": "Indianapolis", "lat": 39.7684, "lng": -86.1581, "radius": 25},
    {"name": "Seattle", "lat": 47.6062, "lng": -122.3321, "radius": 30},
    {"name": "Denver", "lat": 39.7392, "lng": -104.9903, "radius": 35},
    {"name": "Washington", "lat": 38.9072, "lng": -77.0369, "radius": 25}
]

def generate_random_coordinates(city: Dict[str, Any]) -> tuple[float, float]:
    """Generate random coordinates within a city's radius"""
    # Convert radius from km to degrees (approximate)
    lat_radius = city["radius"] / 111.0  # 1 degree latitude ≈ 111 km
    lng_radius = city["radius"] / (111.0 * math.cos(math.radians(city["lat"])))
    
    lat = city["lat"] + random.uniform(-lat_radius, lat_radius)
    lng = city["lng"] + random.uniform(-lng_radius, lng_radius)
    
    return lng, lat  # MongoDB expects [longitude, latitude]

def generate_event_times() -> tuple[datetime, datetime]:
    """Generate realistic event start and end times"""
    # Events can be from 1 month ago to 6 months in the future
    start_range = datetime.utcnow() - timedelta(days=30)
    end_range = datetime.utcnow() + timedelta(days=180)
    
    start_date = start_range + timedelta(
        seconds=random.randint(0, int((end_range - start_range).total_seconds()))
    )
    
    # Event duration: 1-8 hours
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
    
    # Generate tags
    num_tags = random.randint(2, 6)
    event_tags = random.sample(TAGS, num_tags)
    
    # Add category-specific tags
    if category.lower() in ["technology", "science"]:
        event_tags.extend(["technical", "innovation"])
    elif category.lower() in ["music", "arts & culture"]:
        event_tags.extend(["creative", "artistic"])
    elif category.lower() in ["sports", "health & wellness"]:
        event_tags.extend(["fitness", "active"])
    
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
        "tags": list(set(event_tags)),  # Remove duplicates
        "created_at": start_date - timedelta(days=random.randint(1, 30)),
        "updated_at": start_date - timedelta(days=random.randint(1, 30))
    }
    
    return event

def generate_events(count: int = 10000) -> List[Dict[str, Any]]:
    """Generate a list of events"""
    print(f"Generating {count} events...")
    events = []
    
    for i in range(count):
        if (i + 1) % 1000 == 0:
            print(f"Generated {i + 1} events...")
        events.append(generate_event())
    
    return events

def save_to_json(events: List[Dict[str, Any]], filename: str = "test_events.json"):
    """Save events to JSON file"""
    print(f"Saving {len(events)} events to {filename}...")
    
    # Convert datetime objects to ISO strings for JSON serialization
    json_events = []
    for event in events:
        json_event = event.copy()
        json_event["start_date"] = event["start_date"].isoformat()
        json_event["end_date"] = event["end_date"].isoformat()
        json_event["created_at"] = event["created_at"].isoformat()
        json_event["updated_at"] = event["updated_at"].isoformat()
        json_events.append(json_event)
    
    with open(filename, 'w') as f:
        json.dump(json_events, f, indent=2)
    
    print(f"Saved to {filename}")

def main():
    """Main function to generate test data"""
    print("MongoDB Events Demo - Test Data Generator")
    print("=" * 50)
    
    # Generate events
    events = generate_events(10000)
    
    # Save to JSON
    save_to_json(events)
    
    # Print statistics
    print("\nGenerated Event Statistics:")
    print(f"Total events: {len(events)}")
    
    categories = {}
    cities = {}
    for event in events:
        cat = event["category"]
        categories[cat] = categories.get(cat, 0) + 1
        
        # Determine city based on coordinates
        lng, lat = event["location"]["coordinates"]
        for city in CITIES:
            distance = math.sqrt((lat - city["lat"])**2 + (lng - city["lng"])**2)
            if distance < city["radius"] / 111.0:  # Rough conversion
                cities[city["name"]] = cities.get(city["name"], 0) + 1
                break
    
    print(f"Categories: {len(categories)}")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {cat}: {count}")
    
    print(f"Cities: {len(cities)}")
    for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {city}: {count}")
    
    print("\nTest data generation complete!")
    print("You can now import this data into MongoDB using:")
    print("mongoimport --db events_demo --collection events --file test_events.json --jsonArray")

if __name__ == "__main__":
    main()
