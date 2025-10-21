#!/usr/bin/env python3
"""
Test Data Generator for EventSphere
Generates comprehensive test data including events, venues, users, checkins, and reviews
Supports both JSON export and direct MongoDB seeding

Usage:
python generate_test_data.py --seed-db --clear-db
python generate_test_data.py --seed-db --clear-db --events 10000 --venues 500 --users 2000 --tickets 5000 # this will generate all the data and seed the database
python generate_test_data.py --json-only # this will generate all the data and save it to json files

"""

import random
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import math
from bson import ObjectId

# Add app directory to path for config import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from config import Config
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
    print("MongoDB integration available")
except ImportError:
    MONGODB_AVAILABLE = False
    print("Warning: MongoDB integration not available. Install pymongo and ensure config.py is accessible for direct database seeding.")
    
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

# Review-related data
REVIEW_TITLES = [
    "Amazing experience!", "Great event overall", "Could be better", "Highly recommended",
    "Worth attending", "Disappointing", "Excellent organization", "Good value for money",
    "Well worth the time", "Not what I expected", "Fantastic speakers", "Poor venue",
    "Great networking", "Educational and fun", "Overpriced", "Perfect for beginners"
]

REVIEW_TEXTS = [
    "This event exceeded my expectations. The speakers were knowledgeable and engaging, and the networking opportunities were fantastic.",
    "Great event with excellent content. The venue was perfect and the organization was top-notch.",
    "I had a wonderful time at this event. The topics covered were relevant and the community was welcoming.",
    "The event was well-organized and the speakers were experts in their field. I learned a lot and met interesting people.",
    "This was one of the best events I've attended this year. Highly recommend to anyone interested in this topic.",
    "The event was okay, but I expected more interactive sessions. The content was good but could have been more engaging.",
    "Disappointing experience. The event didn't live up to the description and the venue was overcrowded.",
    "Good event overall, but the food was poor and the venue was too noisy. The content was valuable though.",
    "Excellent event with great speakers and well-organized activities. The networking was particularly valuable.",
    "The event was informative but the venue was too small for the number of attendees. Still worth attending.",
    "Fantastic event! The organizers did a great job and the content was exactly what I was looking for.",
    "This event was a waste of time. Poor organization and the speakers were not engaging at all.",
    "Great value for money. The event delivered on its promises and I would definitely attend again.",
    "The event was educational and fun. The interactive sessions were particularly well done.",
    "Good event but overpriced for what was offered. The content was decent but not exceptional.",
    "Perfect for beginners in this field. The speakers explained complex topics in an accessible way."
]

REVIEW_TAGS = [
    "great-venue", "good-food", "excellent-speaker", "well-organized",
    "poor-venue", "bad-food", "disappointing", "disorganized",
    "crowded", "noisy", "expensive", "good-value", "family-friendly",
    "professional", "fun", "educational", "networking", "entertaining"
]

# Major cities with coordinates for realistic geospatial distribution
CITIES = [
    # US Cities
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
    {"name": "Washington", "lat": 38.9072, "lng": -77.0369, "radius": 25},
    
    # Canadian Cities
    {"name": "Vancouver", "lat": 49.1655, "lng": -123.9393, "radius": 10},
    {"name": "Nanaimo", "lat": 49.0831, "lng": -123.9351, "radius": 10},
    {"name": "Duncan", "lat": 48.7777, "lng": -123.7118, "radius": 10},
    {"name": "Victoria", "lat": 48.4284, "lng": -123.3656, "radius": 10},
    {"name": "Toronto", "lat": 43.6532, "lng": -79.3832, "radius": 40},
    {"name": "Montreal", "lat": 45.5017, "lng": -73.5673, "radius": 35},
    {"name": "Calgary", "lat": 51.0447, "lng": -114.0719, "radius": 30},
    {"name": "Ottawa", "lat": 45.4215, "lng": -75.6972, "radius": 25},
    {"name": "Edmonton", "lat": 53.5461, "lng": -113.4938, "radius": 30},
    {"name": "Winnipeg", "lat": 49.8951, "lng": -97.1384, "radius": 25},
    {"name": "Quebec City", "lat": 46.8139, "lng": -71.2080, "radius": 20},
    {"name": "Hamilton", "lat": 43.2557, "lng": -79.8711, "radius": 20},
    {"name": "Kitchener", "lat": 43.4501, "lng": -80.4829, "radius": 15}
]

# Venue data for realistic venue generation - Updated for polymorphic schema
VENUE_TYPES = [
    "conferenceCenter", "park", "restaurant", "virtualSpace", "stadium", "theater"
]

# Legacy venue types for backward compatibility
LEGACY_VENUE_TYPES = [
    "Conference Center", "Convention Center", "Hotel Ballroom", "Community Center",
    "University Auditorium", "Museum", "Gallery", "Theater", "Concert Hall",
    "Sports Arena", "Stadium", "Gymnasium", "Park", "Outdoor Venue",
    "Restaurant", "Bar", "Club", "Library", "Co-working Space", "Office Building",
    "Warehouse", "Studio", "Church", "Temple", "School", "Campus"
]

# Event types for polymorphic schema
EVENT_TYPES = ["inPerson", "virtual", "hybrid", "recurring"]

VENUE_NAMES = {
    "conferenceCenter": [
        "Grand Conference Center", "Metro Convention Hall", "Business Center Plaza",
        "Professional Development Center", "Executive Conference Center"
    ],
    "park": [
        "Central Park", "City Park", "Memorial Park", "Riverside Park",
        "Community Park", "Recreation Park"
    ],
    "restaurant": [
        "Fine Dining Restaurant", "Bistro", "Cafe", "Steakhouse", "Italian Restaurant",
        "Asian Fusion", "Mediterranean Restaurant", "Farm-to-Table Restaurant"
    ],
    "virtualSpace": [
        "Virtual Conference Center", "Online Meeting Space", "Digital Venue",
        "Virtual Event Platform", "Remote Gathering Space"
    ],
    "stadium": [
        "Sports Stadium", "Arena", "Athletic Complex", "Sports Center",
        "Multi-Purpose Stadium", "Convention Stadium"
    ],
    "theater": [
        "Community Theater", "Regional Theater", "Performing Arts Center",
        "Drama Theater", "Black Box Theater", "Historic Theater"
    ],
    # Legacy support
    "Conference Center": [
        "Grand Conference Center", "Metro Convention Hall", "Business Center Plaza",
        "Professional Development Center", "Executive Conference Center"
    ],
    "Convention Center": [
        "City Convention Center", "Metro Convention Center", "Grand Convention Hall",
        "International Convention Center", "Regional Convention Center"
    ],
    "Hotel Ballroom": [
        "Grand Ballroom", "Crystal Ballroom", "Royal Ballroom", "Elegant Ballroom",
        "Prestige Ballroom", "Luxury Ballroom", "Executive Ballroom"
    ],
    "Community Center": [
        "Community Center", "Neighborhood Center", "Civic Center", "Town Hall",
        "Public Center", "Recreation Center"
    ],
    "University Auditorium": [
        "University Auditorium", "Student Center", "Academic Hall", "Lecture Hall",
        "Campus Center", "Education Building"
    ],
    "Museum": [
        "Art Museum", "Science Museum", "History Museum", "Cultural Center",
        "Heritage Museum", "Contemporary Art Gallery"
    ],
    "Theater": [
        "Community Theater", "Regional Theater", "Performing Arts Center",
        "Drama Theater", "Black Box Theater", "Historic Theater"
    ],
    "Concert Hall": [
        "Symphony Hall", "Concert Hall", "Music Center", "Performing Arts Center",
        "Orchestra Hall", "Recital Hall"
    ],
    "Sports Arena": [
        "Sports Complex", "Athletic Center", "Fitness Center", "Sports Arena",
        "Recreation Center", "Athletic Club"
    ],
    "Restaurant": [
        "Fine Dining Restaurant", "Bistro", "Cafe", "Steakhouse", "Italian Restaurant",
        "Asian Fusion", "Mediterranean Restaurant", "Farm-to-Table Restaurant"
    ],
    "Bar": [
        "Craft Cocktail Bar", "Wine Bar", "Sports Bar", "Rooftop Bar", "Speakeasy",
        "Brewery", "Pub", "Lounge"
    ],
    "Club": [
        "Nightclub", "Dance Club", "Music Venue", "Entertainment Club",
        "Social Club", "Private Club"
    ],
    "Park": [
        "Central Park", "City Park", "Memorial Park", "Riverside Park",
        "Community Park", "Recreation Park"
    ],
    "Outdoor Venue": [
        "Amphitheater", "Pavilion", "Garden", "Plaza", "Square",
        "Waterfront", "Beach", "Mountain Venue"
    ]
}

VENUE_AMENITIES = [
    "WiFi", "Parking", "Catering", "Audio/Visual Equipment", "Stage",
    "Lighting", "Air Conditioning", "Heating", "Restrooms", "Accessibility",
    "Kitchen", "Bar", "Outdoor Space", "Balcony", "Elevator", "Security",
    "Storage", "Dressing Rooms", "Green Room", "Reception Area"
]

VENUE_CAPACITIES = {
    # New polymorphic types
    "conferenceCenter": (50, 2000),
    "park": (50, 5000),
    "restaurant": (10, 100),
    "virtualSpace": (10, 10000),
    "stadium": (1000, 100000),
    "theater": (50, 800),
    # Legacy types for backward compatibility
    "Conference Center": (50, 2000),
    "Convention Center": (200, 10000),
    "Hotel Ballroom": (20, 500),
    "Community Center": (10, 200),
    "University Auditorium": (50, 1000),
    "Museum": (20, 300),
    "Gallery": (10, 100),
    "Theater": (50, 800),
    "Concert Hall": (100, 2000),
    "Sports Arena": (100, 20000),
    "Stadium": (1000, 100000),
    "Gymnasium": (20, 500),
    "Park": (50, 5000),
    "Outdoor Venue": (20, 2000),
    "Restaurant": (10, 100),
    "Bar": (20, 200),
    "Club": (50, 1000),
    "Library": (10, 100),
    "Co-working Space": (5, 50),
    "Office Building": (10, 200),
    "Warehouse": (50, 1000),
    "Studio": (5, 50),
    "Church": (20, 500),
    "Temple": (20, 500),
    "School": (10, 200),
    "Campus": (50, 2000)
}

# User data for realistic user generation
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna",
    "Steven", "Carol", "Paul", "Ruth", "Andrew", "Sharon", "Joshua", "Michelle",
    "Kenneth", "Laura", "Kevin", "Sarah", "Brian", "Kimberly", "George", "Deborah",
    "Timothy", "Dorothy", "Ronald", "Lisa", "Jason", "Nancy", "Edward", "Karen",
    "Jeffrey", "Betty", "Ryan", "Helen", "Jacob", "Sandra", "Gary", "Donna",
    "Nicholas", "Carol", "Eric", "Ruth", "Jonathan", "Sharon", "Stephen", "Michelle",
    "Larry", "Laura", "Justin", "Sarah", "Scott", "Kimberly", "Brandon", "Deborah",
    "Benjamin", "Dorothy", "Samuel", "Amy", "Gregory", "Angela", "Alexander", "Ashley"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson"
]

USER_INTERESTS = [
    "Technology", "Music", "Sports", "Food & Drink", "Arts & Culture", "Business",
    "Education", "Health & Wellness", "Entertainment", "Community", "Science",
    "Fashion", "Travel", "Photography", "Gaming", "Networking", "Fitness",
    "Cooking", "Reading", "Movies", "Theater", "Dance", "Painting", "Writing",
    "Volunteering", "Outdoor Activities", "Hiking", "Cycling", "Swimming",
    "Yoga", "Meditation", "Languages", "History", "Politics", "Environment"
]

USER_OCCUPATIONS = [
    "Software Engineer", "Data Scientist", "Product Manager", "Designer", "Marketing Manager",
    "Sales Representative", "Teacher", "Doctor", "Lawyer", "Consultant", "Entrepreneur",
    "Student", "Researcher", "Artist", "Musician", "Writer", "Photographer", "Chef",
    "Event Planner", "Real Estate Agent", "Financial Advisor", "HR Manager", "Project Manager",
    "Business Analyst", "Accountant", "Nurse", "Engineer", "Architect", "Journalist",
    "Social Worker", "Therapist", "Retail Manager", "Restaurant Manager", "Freelancer"
]

# Check-in status options
CHECKIN_STATUSES = ["attending", "checkedIn", "leftEarly", "completed"]

def poisson_approximation(lam: float) -> int:
    """Simple Poisson distribution approximation using exponential distribution"""
    if lam <= 0:
        return 0
    
    # Use exponential distribution to approximate Poisson
    # This is a simple approximation that works well for small to medium lambda values
    k = 0
    p = 1.0
    while p > math.exp(-lam):
        k += 1
        p *= random.random()
    return max(0, k - 1)

# Specific coordinates to ensure some events appear at exact locations
SPECIFIC_COORDINATES = [
    {"lat": 49.1655111990514, "lng": -123.93925511567, "name": "Vancouver Specific Location"},
    {"lat": 43.6532, "lng": -79.3832, "name": "Toronto Downtown"},
    {"lat": 40.7128, "lng": -74.0060, "name": "New York City Center"},
    {"lat": 37.7749, "lng": -122.4194, "name": "San Francisco Downtown"},
    {"lat": 47.6062, "lng": -122.3321, "name": "Seattle Downtown"}
]

def generate_random_coordinates(city: Dict[str, Any]) -> tuple[float, float]:
    """Generate random coordinates within a city's radius"""
    # 20% chance to use exact coordinates for better test data coverage
    if random.random() < 0.2:
        specificCoord = random.choice(SPECIFIC_COORDINATES)
        return specificCoord["lng"], specificCoord["lat"]
    
    # Convert radius from km to degrees (approximate)
    latRadius = city["radius"] / 111.0  # 1 degree latitude ≈ 111 km
    lngRadius = city["radius"] / (111.0 * math.cos(math.radians(city["lat"])))
    
    lat = city["lat"] + random.uniform(-latRadius, latRadius)
    lng = city["lng"] + random.uniform(-lngRadius, lngRadius)
    
    return lng, lat  # MongoDB expects [longitude, latitude]

def generate_venue() -> Dict[str, Any]:
    """Generate a single venue with realistic data using polymorphic schema"""
    venueType = random.choice(VENUE_TYPES)
    city = random.choice(CITIES)
    lng, lat = generate_random_coordinates(city)
    
    # Get appropriate name for venue type
    if venueType in VENUE_NAMES:
        baseName = random.choice(VENUE_NAMES[venueType])
    else:
        baseName = f"{venueType.replace('_', ' ').title()}"
    
    # Add city name to venue
    venue_name = f"{baseName} - {city['name']}"
    
    # Generate amenities based on venue type
    num_amenities = random.randint(3, 8)
    venue_amenities = random.sample(VENUE_AMENITIES, num_amenities)
    
    # Add type-specific amenities
    if venueType in ["Conference Center", "Convention Center"]:
        venue_amenities.extend(["Audio/Visual Equipment", "Stage", "Catering"])
    elif venueType in ["Restaurant", "Bar"]:
        venue_amenities.extend(["Kitchen", "Bar"])
    elif venueType in ["Sports Arena", "Gymnasium"]:
        venue_amenities.extend(["Storage", "Dressing Rooms"])
    elif venueType in ["Theater", "Concert Hall"]:
        venue_amenities.extend(["Stage", "Lighting", "Dressing Rooms", "Green Room"])
    
    # Get capacity range for venue type
    min_capacity, max_capacity = VENUE_CAPACITIES.get(venueType, (10, 100))
    capacity = random.randint(min_capacity, max_capacity)
    
    # Generate contact information
    phone = f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
    email = f"info@{baseName.lower().replace(' ', '')}.com"
    
    venue = {
        "name": venue_name,
        "venueType": venueType,  # Polymorphic discriminator
        "schemaVersion": "1.0",    # Schema versioning
        "type": venueType.replace('_', ' ').title(),  # Legacy type field
        "description": f"A {venueType.replace('_', ' ')} located in {city['name']}, perfect for various events and gatherings.",
        "location": {
            "type": "Point",
            "coordinates": [lng, lat]
        },
        "address": {
            "street": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'Cedar', 'Maple'])} St",
            "city": city["name"],
            "state": random.choice(["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]),
            "zipCode": f"{random.randint(10000, 99999)}",
            "country": "USA"
        },
        "capacity": capacity,
        "amenities": list(set(venue_amenities)),  # Remove duplicates
        "contact": {
            "phone": phone,
            "email": email,
            "website": f"https://www.{baseName.lower().replace(' ', '')}.com"
        },
        "pricing": {
            "hourlyRate": random.randint(50, 500),
            "dailyRate": random.randint(200, 2000),
            "currency": "USD"
        },
        "availability": {
            "monday": {"open": "09:00", "close": "22:00"},
            "tuesday": {"open": "09:00", "close": "22:00"},
            "wednesday": {"open": "09:00", "close": "22:00"},
            "thursday": {"open": "09:00", "close": "22:00"},
            "friday": {"open": "09:00", "close": "23:00"},
            "saturday": {"open": "10:00", "close": "23:00"},
            "sunday": {"open": "10:00", "close": "20:00"}
        },
        "rating": round(random.uniform(3.0, 5.0), 1),
        "reviewCount": random.randint(0, 200),
        "createdAt": datetime.now(timezone.utc) - timedelta(days=random.randint(30, 365)),
        "updatedAt": datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))
    }
    
    # Add polymorphic type-specific details
    if venueType == "conferenceCenter":
        venue["conferenceCenterDetails"] = {
            "breakoutRooms": random.randint(2, 12),
            "avEquipment": random.sample(["Projectors", "Microphones", "Video Conferencing", "Whiteboards", "Sound System"], random.randint(2, 4)),
            "cateringAvailable": random.choice([True, False])
        }
    elif venueType == "park":
        venue["parkDetails"] = {
            "outdoorSpace": True,
            "parkingSpaces": random.randint(50, 500),
            "restroomFacilities": random.choice([True, False])
        }
    elif venueType == "virtualSpace":
        venue["virtualSpaceDetails"] = {
            "platform": random.choice(["Zoom", "Teams", "WebEx", "Custom Platform"]),
            "maxConcurrentUsers": random.randint(100, 10000),
            "recordingCapability": random.choice([True, False])
        }
    
    # Add computed stats (Computed Pattern)
    totalEventsHosted = random.randint(0, 100)
    # Fix: Ensure averageAttendance is always valid
    if capacity and capacity > 20:
        averageAttendance = random.randint(20, capacity)
    elif capacity and capacity <= 20:
        averageAttendance = random.randint(1, capacity)  # Use full capacity range for small venues
    else:
        averageAttendance = random.randint(20, 200)  # Default range when no capacity
    revenueGenerated = random.randint(5000, 50000)
    lastEventDate = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90))
    
    venue["computedStats"] = {
        "totalEventsHosted": totalEventsHosted,
        "averageAttendance": averageAttendance,
        "revenueGenerated": revenueGenerated,
        "lastEventDate": lastEventDate,
        "lastUpdated": datetime.now(timezone.utc)
    }
    
    return venue

def generate_venues(count: int = 500) -> List[Dict[str, Any]]:
    """Generate a list of venues"""
    print(f"Generating {count} venues...")
    venues = []
    
    for i in range(count):
        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1} venues...")
        venue = generate_venue()
        # Add _id for MongoDB compatibility
        venue["_id"] = ObjectId()
        venues.append(venue)
    
    return venues

def generate_user() -> Dict[str, Any]:
    """Generate a single user with realistic data"""
    firstName = random.choice(FIRST_NAMES)
    lastName = random.choice(LAST_NAMES)
    # Add random number to ensure unique emails
    email = f"{firstName.lower()}.{lastName.lower()}{random.randint(1, 9999)}@{random.choice(['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'])}"
    
    # Generate interests
    num_interests = random.randint(3, 8)
    user_interests = random.sample(USER_INTERESTS, num_interests)
    
    # Generate location
    city = random.choice(CITIES)
    lng, lat = generate_random_coordinates(city)
    
    # Generate age (18-65)
    age = random.randint(18, 65)
    
    # Generate join date (within last 2 years)
    join_date = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 730))
    
    user = {
        "email": email,
        "schemaVersion": "1.0",  # Schema versioning
        "profile": {
            "firstName": firstName,
            "lastName": lastName,
            "preferences": {
                "categories": user_interests[:5],  # Top 5 interests as preferred event types
                "location": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "radiusKm": random.randint(5, 50)
            }
        },
        "createdAt": join_date,
        "updatedAt": join_date,  # Initially same as createdAt
        "lastLogin": join_date + timedelta(days=random.randint(1, 30)) if random.random() < 0.8 else None
    }
    
    return user

def generate_users(count: int = 2000) -> List[Dict[str, Any]]:
    """Generate a list of users"""
    print(f"Generating {count} users...")
    users = []
    
    for i in range(count):
        if (i + 1) % 200 == 0:
            print(f"Generated {i + 1} users...")
        user = generate_user()
        # Add _id for MongoDB compatibility
        user["_id"] = ObjectId()
        users.append(user)
    
    return users

def generate_checkin(userId: str, eventId: str, event_start: datetime, event_end: datetime, event_location: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate a single check-in with realistic data"""
    # Check-in time is typically around event start time
    checkInTime = event_start + timedelta(minutes=random.randint(-30, 60))
    
    # Status based on timing
    if checkInTime < event_start:
        status = "attending"
    elif checkInTime <= event_start + timedelta(hours=1):
        status = "checkedIn"
    elif checkInTime < event_end - timedelta(hours=1):
        status = "leftEarly"
    else:
        status = "completed"
    
    # Generate location based on event location (slightly offset for realism)
    if event_location and "coordinates" in event_location:
        event_lng, event_lat = event_location["coordinates"]
        # Small offset for realism (within ~100m)
        offset_lat = random.uniform(-0.001, 0.001)
        offset_lng = random.uniform(-0.001, 0.001)
        checkin_lng = event_lng + offset_lng
        checkin_lat = event_lat + offset_lat
    else:
        # Fallback to random coordinates if no event location
        checkin_lng = random.uniform(-180, 180)
        checkin_lat = random.uniform(-90, 90)
    
    checkin = {
        "eventId": ObjectId(eventId),
        "userId": ObjectId(userId),
        "venueId": ObjectId(),  # Placeholder - would need actual venueId
        "checkInTime": checkInTime,
        "qrCode": f"QR-{random.randint(100000, 999999)}",
        "schemaVersion": "1.0",  # Schema versioning
        "ticketTier": random.choice(["General Admission", "VIP", "Early Bird"]) if random.random() < 0.7 else None,
        "checkInMethod": random.choice(["qrCode", "manual", "mobile_app"]),
        "location": {
            "type": "Point",
            "coordinates": [checkin_lng, checkin_lat]
        },
        "metadata": {
            "deviceInfo": random.choice(["iPhone", "Android", "Web Browser", "Tablet"]) if random.random() < 0.8 else None,
            "ipAddress": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}" if random.random() < 0.5 else None,
            "staffVerified": random.choice([True, False])
        },
        "createdAt": checkInTime,
        "updatedAt": checkInTime  # Initially same as createdAt
    }
    
    return checkin

def generate_checkins(users: List[Dict[str, Any]], events: List[Dict[str, Any]], checkins_per_user: float = 2.5) -> List[Dict[str, Any]]:
    """Generate check-ins for users and events"""
    print(f"Generating check-ins for {len(users)} users and {len(events)} events...")
    checkins = []
    
    for i, user in enumerate(users):
        if (i + 1) % 200 == 0:
            print(f"Generated check-ins for {i + 1} users...")
        
        # Number of check-ins per user (Poisson distribution)
        num_checkins = poisson_approximation(checkins_per_user)
        
        # Select random events for this user
        user_events = random.sample(events, min(num_checkins, len(events)))
        
        for event in user_events:
            checkin = generate_checkin(
                user["_id"],  # Use actual user _id
                event["_id"],  # Use actual event _id
                event["startDate"],
                event["endDate"],
                event.get("location")  # Pass event location
            )
            # Add _id for MongoDB compatibility
            checkin["_id"] = ObjectId()
            checkins.append(checkin)
    
    return checkins

def generate_event_times() -> tuple[datetime, datetime]:
    """Generate realistic event start and end times"""
    # Events can be from 1 month ago to 6 months in the future
    start_range = datetime.now(timezone.utc) - timedelta(days=30)
    end_range = datetime.now(timezone.utc) + timedelta(days=180)
    
    startDate = start_range + timedelta(
        seconds=random.randint(0, int((end_range - start_range).total_seconds()))
    )
    
    # Event duration: 1-8 hours
    duration_hours = random.randint(1, 8)
    endDate = startDate + timedelta(hours=duration_hours)
    
    return startDate, endDate

def generate_event(venueId: str = None, venue_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate a single event with realistic data using polymorphic schema"""
    category = random.choice(CATEGORIES)
    eventType = random.choice(EVENT_TYPES)  # Polymorphic discriminator
    city = random.choice(CITIES)
    lng, lat = generate_random_coordinates(city)
    startDate, endDate = generate_event_times()
    
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
    
    # Generate pricing
    isFree = random.random() < 0.4  # 40% free events
    if isFree:
        price = 0
    else:
        price = random.randint(10, 200)
    
    event = {
        "title": title,
        "description": random.choice(DESCRIPTIONS),
        "category": category,
        "eventType": eventType,  # Polymorphic discriminator
        "schemaVersion": "1.0",    # Schema versioning
        "location": {
            "type": "Point",
            "coordinates": [lng, lat]
        },
        "venueId": ObjectId(venueId) if venueId else None,
        "venueReference": {
            "name": venue_data["name"],
            "city": venue_data["address"]["city"],
            "capacity": venue_data["capacity"],
            "venueType": venue_data["venueType"]
        } if venue_data else None,
        "startDate": startDate,
        "endDate": endDate,
        "organizer": random.choice(ORGANIZERS),
        "maxAttendees": random.randint(10, 1000) if random.random() < 0.8 else None,
        "currentAttendees": random.randint(0, 50),  # Some events already have attendees
        "price": price,
        "currency": "USD",
        "isFree": isFree,
        "status": random.choice(["draft", "published", "cancelled", "completed"]),
        "tags": list(set(event_tags)),  # Remove duplicates
        "createdAt": startDate - timedelta(days=random.randint(1, 30)),
        "updatedAt": startDate - timedelta(days=random.randint(1, 30))
    }
    
    # Add polymorphic type-specific details
    if eventType == "virtual":
        event["virtualDetails"] = {
            "platform": random.choice(["Zoom", "Teams", "WebEx", "YouTube Live", "Twitch"]),
            "meetingUrl": f"https://{random.choice(['zoom.us', 'teams.microsoft.com', 'webex.com'])}/j/{random.randint(100000000, 999999999)}",
            "recordingAvailable": random.choice([True, False]),
            "timezone": random.choice(["UTC", "EST", "PST", "CST", "MST"])
        }
    elif eventType == "hybrid":
        event["hybridDetails"] = {
            "virtualCapacity": random.randint(50, 1000),
            "inPersonCapacity": random.randint(20, 500),
            "virtual_meetingUrl": f"https://{random.choice(['zoom.us', 'teams.microsoft.com'])}/j/{random.randint(100000000, 999999999)}"
        }
    elif eventType == "recurring":
        event["recurringDetails"] = {
            "frequency": random.choice(["daily", "weekly", "monthly", "yearly"]),
            "endRecurrence": startDate + timedelta(days=random.randint(30, 365)),
            "exceptions": [startDate + timedelta(days=random.randint(1, 30)) for _ in range(random.randint(0, 3))]
        }
    
    # Add general metadata
    event["metadata"] = {
        "ageRestriction": random.choice(["All Ages", "18+", "21+", "13+"]) if random.random() < 0.3 else None,
        "dressCode": random.choice(["Casual", "Business Casual", "Formal", "Black Tie"]) if random.random() < 0.2 else None,
        "accessibilityFeatures": random.sample(["Wheelchair Accessible", "Sign Language Interpreter", "Live Captioning", "Audio Description"], random.randint(0, 2)) if random.random() < 0.4 else []
    }
    
    # Add computed stats (Computed Pattern)
    maxAttendees = event.get("maxAttendees", 100)  # Default to 100 if not set
    if maxAttendees is None:
        maxAttendees = 100  # Ensure we have a valid number
    totalTicketsSold = random.randint(0, maxAttendees)
    totalRevenue = totalTicketsSold * price if not isFree else 0
    attendanceRate = (totalTicketsSold / maxAttendees * 100) if maxAttendees > 0 else 0
    
    event["computedStats"] = {
        "totalTicketsSold": totalTicketsSold,
        "totalRevenue": totalRevenue,
        "attendanceRate": round(attendanceRate, 2),
        "reviewCount": random.randint(0, 50),
        "averageRating": round(random.uniform(3.0, 5.0), 1),
        "lastUpdated": datetime.now(timezone.utc)
    }
    
    # Generate embedded tickets for the event
    event["tickets"] = generate_event_tickets(event)
    
    return event

def generate_events(count: int = 10000, venues: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Generate a list of events"""
    print(f"Generating {count} events...")
    events = []
    
    # Ensure some events are created at specific coordinates
    specific_events_count = min(50, count // 20)  # 5% of events or max 50
    
    for i in range(count):
        if (i + 1) % 1000 == 0:
            print(f"Generated {i + 1} events...")
        
        # 70% of events have venues, 30% are at custom locations
        venueId = None
        selected_venue = None
        if venues and random.random() < 0.7:
            selected_venue = random.choice(venues)
            venueId = selected_venue["_id"]  # Use actual venue _id
        
        event = generate_event(venueId, selected_venue)
        
        # For the first few events, ensure they're at specific coordinates
        if i < specific_events_count:
            specificCoord = SPECIFIC_COORDINATES[i % len(SPECIFIC_COORDINATES)]
            event["location"] = {
                "type": "Point",
                "coordinates": [specificCoord["lng"], specificCoord["lat"]]
            }
            # Update event title to indicate it's at a specific location
            event["title"] = f"{event['title']} - {specificCoord['name']}"
        
        # Add _id for MongoDB compatibility
        event["_id"] = ObjectId()
        events.append(event)
    
    return events

def generate_review(eventId: str, userId: str, event_date: datetime) -> Dict[str, Any]:
    """Generate a single review with realistic data"""
    # Reviews are typically written after the event
    review_date = event_date + timedelta(days=random.randint(1, 30))
    
    # Rating distribution: mostly positive (4-5 stars), some neutral (3), few negative (1-2)
    rating_weights = [0.05, 0.1, 0.15, 0.35, 0.35]  # 1, 2, 3, 4, 5 stars
    rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]
    
    # Select review text based on rating
    if rating >= 4:
        review_text = random.choice(REVIEW_TEXTS[:8])  # Positive reviews
        title = random.choice(REVIEW_TITLES[:8])
    elif rating == 3:
        review_text = random.choice(REVIEW_TEXTS[8:12])  # Neutral reviews
        title = random.choice(REVIEW_TITLES[8:12])
    else:
        review_text = random.choice(REVIEW_TEXTS[12:])  # Negative reviews
        title = random.choice(REVIEW_TITLES[12:])
    
    # Generate tags based on rating and content
    num_tags = random.randint(1, 4)
    if rating >= 4:
        # Positive tags
        available_tags = [tag for tag in REVIEW_TAGS if tag in [
            "great-venue", "good-food", "excellent-speaker", "well-organized",
            "good-value", "family-friendly", "professional", "fun", 
            "educational", "networking", "entertaining"
        ]]
    elif rating == 3:
        # Neutral tags
        available_tags = [tag for tag in REVIEW_TAGS if tag in [
            "professional", "educational", "networking"
        ]]
    else:
        # Negative tags
        available_tags = [tag for tag in REVIEW_TAGS if tag in [
            "poor-venue", "bad-food", "disappointing", "disorganized",
            "crowded", "noisy", "expensive"
        ]]
    
    review_tags = random.sample(available_tags, min(num_tags, len(available_tags)))
    
    # Helpful votes (most reviews have few votes, some have many)
    helpful_votes = 0
    if random.random() < 0.3:  # 30% chance of having votes
        helpful_votes = random.randint(1, 50)
    
    # Verified attendee (most reviews are from verified attendees)
    verified_attendee = random.random() < 0.8
    
    review = {
        "eventId": ObjectId(eventId),
        "userId": ObjectId(userId),
        "rating": rating,
        "comment": review_text,
        "schemaVersion": "1.0",  # Schema versioning
        "createdAt": review_date,
        "updatedAt": review_date if random.random() < 0.1 else None  # 10% have updates
    }
    
    return review

def generate_reviews(events: List[Dict[str, Any]], users: List[Dict[str, Any]], reviews_per_event: float = 0.3) -> List[Dict[str, Any]]:
    """Generate reviews for events"""
    print(f"Generating reviews for {len(events)} events...")
    reviews = []
    
    for i, event in enumerate(events):
        if (i + 1) % 1000 == 0:
            print(f"Generated reviews for {i + 1} events...")
        
        # Number of reviews per event (some events have no reviews, some have many)
        num_reviews = poisson_approximation(reviews_per_event * 10)  # Poisson distribution
        
        for _ in range(num_reviews):
            user = random.choice(users)
            review = generate_review(
                event["_id"],  # Use actual event _id
                user["_id"],   # Use actual user _id
                event["startDate"]
            )
            # Add _id for MongoDB compatibility
            review["_id"] = ObjectId()
            reviews.append(review)
    
    return reviews

def save_to_json(events: List[Dict[str, Any]], filename: str = "test_events.json"):
    """Save events to JSON file"""
    print(f"Saving {len(events)} events to {filename}...")
    
    # Convert datetime objects and ObjectIds to strings for JSON serialization
    json_events = []
    for event in events:
        json_event = event.copy()
        json_event["_id"] = str(event["_id"])
        if event.get("venueId"):
            json_event["venueId"] = str(event["venueId"])
        json_event["startDate"] = event["startDate"].isoformat()
        if event.get("endDate"):
            json_event["endDate"] = event["endDate"].isoformat()
        json_event["createdAt"] = event["createdAt"].isoformat()
        json_event["updatedAt"] = event["updatedAt"].isoformat()
        
        # Convert any other datetime fields that might exist (including nested ones)
        def convert_datetime_to_iso(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_datetime_to_iso(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime_to_iso(item) for item in obj]
            else:
                return obj
        
        # Apply datetime conversion to the entire event
        json_event = convert_datetime_to_iso(json_event)
        
        # Convert computedStats datetime fields
        if "computedStats" in event and event["computedStats"]:
            json_event["computedStats"] = event["computedStats"].copy()
            if "lastUpdated" in json_event["computedStats"]:
                json_event["computedStats"]["lastUpdated"] = json_event["computedStats"]["lastUpdated"].isoformat()
        
        json_events.append(json_event)
    
    with open(filename, 'w') as f:
        json.dump(json_events, f, indent=2)
    
    print(f"Saved to {filename}")

def save_reviews_to_json(reviews: List[Dict[str, Any]], filename: str = "test_reviews.json"):
    """Save reviews to JSON file"""
    print(f"Saving {len(reviews)} reviews to {filename}...")
    
    # Convert datetime objects and ObjectIds to strings for JSON serialization
    json_reviews = []
    for review in reviews:
        json_review = review.copy()
        json_review["_id"] = str(review["_id"])
        json_review["eventId"] = str(review["eventId"])
        json_review["userId"] = str(review["userId"])
        json_review["createdAt"] = review["createdAt"].isoformat()
        if review["updatedAt"]:
            json_review["updatedAt"] = review["updatedAt"].isoformat()
        json_reviews.append(json_review)
    
    with open(filename, 'w') as f:
        json.dump(json_reviews, f, indent=2)
    
    print(f"Saved to {filename}")

def save_venues_to_json(venues: List[Dict[str, Any]], filename: str = "test_venues.json"):
    """Save venues to JSON file"""
    print(f"Saving {len(venues)} venues to {filename}...")
    
    # Convert datetime objects and ObjectIds to strings for JSON serialization
    json_venues = []
    for venue in venues:
        json_venue = venue.copy()
        json_venue["_id"] = str(venue["_id"])
        json_venue["createdAt"] = venue["createdAt"].isoformat()
        json_venue["updatedAt"] = venue["updatedAt"].isoformat()
        
        # Convert computedStats datetime fields
        if "computedStats" in venue and venue["computedStats"]:
            json_venue["computedStats"] = venue["computedStats"].copy()
            if "lastEventDate" in json_venue["computedStats"]:
                json_venue["computedStats"]["lastEventDate"] = json_venue["computedStats"]["lastEventDate"].isoformat()
            if "lastUpdated" in json_venue["computedStats"]:
                json_venue["computedStats"]["lastUpdated"] = json_venue["computedStats"]["lastUpdated"].isoformat()
        
        json_venues.append(json_venue)
    
    with open(filename, 'w') as f:
        json.dump(json_venues, f, indent=2)
    
    print(f"Saved to {filename}")

def save_users_to_json(users: List[Dict[str, Any]], filename: str = "test_users.json"):
    """Save users to JSON file"""
    print(f"Saving {len(users)} users to {filename}...")
    
    # Convert datetime objects and ObjectIds to strings for JSON serialization
    json_users = []
    for user in users:
        json_user = user.copy()
        json_user["_id"] = str(user["_id"])
        json_user["createdAt"] = user["createdAt"].isoformat()
        json_user["updatedAt"] = user["updatedAt"].isoformat()
        if user.get("lastLogin"):
            json_user["lastLogin"] = user["lastLogin"].isoformat()
        json_users.append(json_user)
    
    with open(filename, 'w') as f:
        json.dump(json_users, f, indent=2)
    
    print(f"Saved to {filename}")

def save_checkins_to_json(checkins: List[Dict[str, Any]], filename: str = "test_checkins.json"):
    """Save check-ins to JSON file"""
    print(f"Saving {len(checkins)} check-ins to {filename}...")
    
    # Convert datetime objects and ObjectIds to strings for JSON serialization
    json_checkins = []
    for checkin in checkins:
        json_checkin = checkin.copy()
        json_checkin["_id"] = str(checkin["_id"])
        json_checkin["userId"] = str(checkin["userId"])
        json_checkin["eventId"] = str(checkin["eventId"])
        if checkin.get("venueId"):
            json_checkin["venueId"] = str(checkin["venueId"])
        json_checkin["checkInTime"] = checkin["checkInTime"].isoformat()
        json_checkin["createdAt"] = checkin["createdAt"].isoformat()
        json_checkin["updatedAt"] = checkin["updatedAt"].isoformat()
        json_checkins.append(json_checkin)
    
    with open(filename, 'w') as f:
        json.dump(json_checkins, f, indent=2)
    
    print(f"Saved to {filename}")

def generate_event_tickets(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate embedded EventTickets (ticket types available for the event)"""
    # Most events have 1-3 ticket tiers
    num_tiers = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
    tickets = []
    
    base_price = event.get("price", 0)
    
    for i in range(num_tiers):
        if num_tiers == 1:
            tier_name = "General Admission"
        elif i == 0:
            tier_name = "Early Bird"
        elif i == 1:
            tier_name = "General Admission"
        else:
            tier_name = "VIP"
        
        # Calculate tier pricing
        if base_price == 0:
            tier_price = 0
        else:
            if tier_name == "Early Bird":
                tier_price = max(0, base_price * 0.8)  # 20% discount
            elif tier_name == "VIP":
                tier_price = base_price * 1.5  # 50% premium
            else:
                tier_price = base_price
        
        # Generate availability and sold counts
        max_available = random.randint(10, 200)
        sold = random.randint(0, int(max_available * 0.8))  # Up to 80% sold
        
        ticket = {
            "tier": tier_name,
            "price": tier_price,
            "available": max_available - sold,
            "sold": sold
        }
        tickets.append(ticket)
    
    return tickets

def generate_user_tickets(events: List[Dict[str, Any]], users: List[Dict[str, Any]], ticket_count: int = 5000) -> List[Dict[str, Any]]:
    """Generate separate Ticket collection (actual user purchases)"""
    print(f"Generating {ticket_count} user ticket purchases...")
    tickets = []
    
    for i in range(ticket_count):
        if (i + 1) % 500 == 0:
            print(f"Generated {i + 1} ticket purchases...")
        
        event = random.choice(events)
        user = random.choice(users)
        
        # Only generate tickets for events that have pricing
        if event.get("price", 0) > 0:
            price_paid = event["price"]
        else:
            price_paid = 0
        
        ticket = {
            "_id": ObjectId(),
            "eventId": event["_id"],
            "userId": user["_id"],
            "pricePaid": price_paid,
            "status": random.choices(
                ["active", "cancelled", "used"],
                weights=[80, 10, 10]
            )[0],
            "purchasedAt": event["startDate"] - timedelta(days=random.randint(1, 30)),
            "createdAt": datetime.now(timezone.utc) - timedelta(days=random.randint(1, 60))
        }
        tickets.append(ticket)
    
    return tickets

def save_tickets_to_json(tickets: List[Dict[str, Any]], filename: str = "test_tickets.json"):
    """Save user tickets to JSON file"""
    print(f"Saving {len(tickets)} user tickets to {filename}...")
    
    # Convert datetime objects and ObjectIds to strings for JSON serialization
    json_tickets = []
    for ticket in tickets:
        json_ticket = ticket.copy()
        json_ticket["_id"] = str(ticket["_id"])
        json_ticket["eventId"] = str(ticket["eventId"])
        json_ticket["userId"] = str(ticket["userId"])
        json_ticket["purchasedAt"] = ticket["purchasedAt"].isoformat()
        json_ticket["createdAt"] = ticket["createdAt"].isoformat()
        json_tickets.append(json_ticket)
    
    with open(filename, 'w') as f:
        json.dump(json_tickets, f, indent=2)
    
    print(f"Saved to {filename}")

def seed_database(venues, users, events, tickets, checkins, reviews, clear_existing: bool = True):
    """Seed MongoDB database with provided data"""
    if not MONGODB_AVAILABLE:
        print("Error: MongoDB integration not available. Cannot seed database.")
        return False
    
    try:
        print(f"Seeding database: {Config.DB_NAME}")
        client = MongoClient(Config.MONGODB_URI)
        print(f"Using connection: {Config.MONGODB_URI}")
        db = client[Config.DB_NAME]
        
        if clear_existing:
            # Clear existing data
            print("\nClearing existing data...")
            db.events.drop()
            db.venues.drop()
            db.users.drop()
            db.checkins.drop()
            db.reviews.drop()
            # Clear tickets collection (user purchases)
            db.tickets.drop()
            print("✓ Existing data cleared")
        
        # Insert data into MongoDB
        print("\nInserting data into MongoDB...")
        
        try:
            print("Inserting venues...")
            result = db.venues.insert_many(venues)
            print(f"✓ Inserted {len(result.inserted_ids)} venues")
        except Exception as e:
            print(f"❌ Failed to insert venues: {e}")
            raise
        
        try:
            print("Inserting users...")
            result = db.users.insert_many(users)
            print(f"✓ Inserted {len(result.inserted_ids)} users")
        except Exception as e:
            print(f"❌ Failed to insert users: {e}")
            raise
        
        try:
            print("Inserting events...")
            result = db.events.insert_many(events)
            print(f"✓ Inserted {len(result.inserted_ids)} events")
        except Exception as e:
            print(f"❌ Failed to insert events: {e}")
            print("This might be due to validation errors. Check your event schema.")
            raise
        
        try:
            print("Inserting user tickets...")
            result = db.tickets.insert_many(tickets)
            print(f"✓ Inserted {len(result.inserted_ids)} user tickets")
        except Exception as e:
            print(f"❌ Failed to insert user tickets: {e}")
            raise
        
        try:
            print("Inserting checkins...")
            result = db.checkins.insert_many(checkins)
            print(f"✓ Inserted {len(result.inserted_ids)} checkins")
        except Exception as e:
            print(f"❌ Failed to insert checkins: {e}")
            raise
        
        try:
            print("Inserting reviews...")
            result = db.reviews.insert_many(reviews)
            print(f"✓ Inserted {len(result.inserted_ids)} reviews")
        except Exception as e:
            print(f"❌ Failed to insert reviews: {e}")
            raise
        
        print("\n✅ Database seeded successfully!")
        
        # Display summary
        print("\nData Summary:")
        for collection_name in ["venues", "users", "events", "tickets", "checkins", "reviews"]:
            count = db[collection_name].count_documents({})
            print(f"  {collection_name}: {count} documents")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        return False

def main():
    """Main function to generate comprehensive test data"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate comprehensive test data for EventSphere')
    parser.add_argument('--seed-db', action='store_true', help='Seed MongoDB database directly')
    parser.add_argument('--json-only', action='store_true', help='Generate JSON files only (default)')
    parser.add_argument('--clear-db', action='store_true', default=True, help='Clear existing database data before seeding')
    parser.add_argument('--venues', type=int, default=500, help='Number of venues to generate')
    parser.add_argument('--users', type=int, default=2000, help='Number of users to generate')
    parser.add_argument('--events', type=int, default=10000, help='Number of events to generate')
    parser.add_argument('--tickets', type=int, default=5000, help='Number of user ticket purchases to generate')
    
    args = parser.parse_args()
    
    print("EventSphere - Comprehensive Test Data Generator")
    print("=" * 60)
    
    # Generate data
    print(f"\n1. Generating {args.venues} Venues...")
    venues = generate_venues(args.venues)
    
    print(f"\n2. Generating {args.users} Users...")
    users = generate_users(args.users)
    
    print(f"\n3. Generating {args.events} Events (with embedded ticket types)...")
    events = generate_events(args.events, venues)
    
    print(f"\n4. Generating {args.tickets} User Ticket Purchases...")
    tickets = generate_user_tickets(events, users, args.tickets)
    
    print("\n5. Generating Reviews...")
    reviews = generate_reviews(events, users, reviews_per_event=0.4)
    
    print("\n6. Generating Check-ins...")
    checkins = generate_checkins(users, events, checkins_per_user=2.5)
    
    # Handle output based on arguments
    if args.seed_db and MONGODB_AVAILABLE:
        print("\n7. Seeding MongoDB Database...")
        success = seed_database(venues, users, events, tickets, checkins, reviews, clear_existing=args.clear_db)
        if success:
            print("✅ Database seeding completed successfully!")
        else:
            print("❌ Database seeding failed!")
    elif args.seed_db and not MONGODB_AVAILABLE:
        print("\n❌ Cannot seed database: MongoDB integration not available")
        print("Falling back to JSON export...")
        args.json_only = True
    
    if args.json_only or not args.seed_db:
        print("\n7. Saving Data to JSON Files...")
        save_venues_to_json(venues)
        save_users_to_json(users)
        save_to_json(events)
        save_tickets_to_json(tickets)
        save_reviews_to_json(reviews)
        save_checkins_to_json(checkins)
    
    # Print comprehensive statistics
    print("\n" + "=" * 60)
    print("GENERATED DATA STATISTICS")
    print("=" * 60)
    
    # Venue statistics
    print(f"\nVenues: {len(venues)}")
    venueTypes = {}
    for venue in venues:
        venueType = venue["type"]
        venueTypes[venueType] = venueTypes.get(venueType, 0) + 1
    
    print("Top venue types:")
    for venueType, count in sorted(venueTypes.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {venueType}: {count}")
    
    # User statistics
    print(f"\nUsers: {len(users)}")
    users_with_login = sum(1 for user in users if user.get("lastLogin"))
    print(f"Users with login activity: {users_with_login} ({users_with_login/len(users)*100:.1f}%)")
    
    # Event statistics
    print(f"\nEvents: {len(events)}")
    categories = {}
    free_events = sum(1 for event in events if event["isFree"])
    events_with_venues = sum(1 for event in events if event["venueId"] is not None)
    
    for event in events:
        cat = event["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"Free events: {free_events} ({free_events/len(events)*100:.1f}%)")
    print(f"Events with venues: {events_with_venues} ({events_with_venues/len(events)*100:.1f}%)")
    print("Top categories:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {cat}: {count}")
    
    # EventTicket statistics (embedded in events)
    total_event_tickets = sum(len(event.get("tickets", [])) for event in events)
    print(f"\nEventTicket Types (embedded in events): {total_event_tickets}")
    
    # Count ticket tiers
    ticketTiers = {}
    for event in events:
        for ticket in event.get("tickets", []):
            tier = ticket["tier"]
            ticketTiers[tier] = ticketTiers.get(tier, 0) + 1
    
    print("EventTicket tier distribution:")
    for tier, count in sorted(ticketTiers.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_event_tickets) * 100 if total_event_tickets > 0 else 0
        print(f"  {tier}: {count} ({percentage:.1f}%)")
    
    # User Ticket statistics (separate collection)
    print(f"\nUser Ticket Purchases: {len(tickets)}")
    ticket_statuses = {}
    for ticket in tickets:
        status = ticket["status"]
        ticket_statuses[status] = ticket_statuses.get(status, 0) + 1
    
    print("User ticket status distribution:")
    for status, count in sorted(ticket_statuses.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(tickets)) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    # Review statistics
    print(f"\nReviews: {len(reviews)}")
    ratings = {}
    for review in reviews:
        rating = review["rating"]
        ratings[rating] = ratings.get(rating, 0) + 1
    
    print("Rating distribution:")
    for rating in sorted(ratings.keys()):
        count = ratings[rating]
        percentage = (count / len(reviews)) * 100
        print(f"  {rating} stars: {count} ({percentage:.1f}%)")
    
    # Note: verified_attendee field not implemented in current review generation
    print(f"Total reviews: {len(reviews)}")
    
    # Check-in statistics
    print(f"\nCheck-ins: {len(checkins)}")
    checkin_methods = {}
    for checkin in checkins:
        method = checkin.get("checkInMethod", "unknown")
        checkin_methods[method] = checkin_methods.get(method, 0) + 1
    
    print("Check-in method distribution:")
    for method, count in sorted(checkin_methods.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(checkins)) * 100
        print(f"  {method}: {count} ({percentage:.1f}%)")
    
    if args.json_only or not args.seed_db:
        print("\n" + "=" * 60)
        print("IMPORT COMMANDS FOR MONGODB")
        print("=" * 60)
        print("You can now import this data into MongoDB using:")
        print("mongoimport --db events_demo --collection venues --file test_venues.json --jsonArray")
        print("mongoimport --db events_demo --collection users --file test_users.json --jsonArray")
        print("mongoimport --db events_demo --collection events --file test_events.json --jsonArray")
        print("mongoimport --db events_demo --collection tickets --file test_tickets.json --jsonArray")
        print("mongoimport --db events_demo --collection reviews --file test_reviews.json --jsonArray")
        print("mongoimport --db events_demo --collection checkins --file test_checkins.json --jsonArray")
        print("Note: Events contain embedded EventTickets (ticket types), tickets collection contains user purchases")
    
    print("\n✅ Test data generation complete!")

if __name__ == "__main__":
    main()
