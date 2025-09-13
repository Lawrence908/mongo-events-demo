#!/usr/bin/env python3
"""
Data synthesis script using Faker to generate sample events
"""
import os
import random
import sys
from datetime import timedelta

from faker import Faker

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_mongodb
from app.models import EventCreate
from app.services import get_event_service

fake = Faker()

# Event categories
CATEGORIES = [
    "conference",
    "workshop",
    "meetup",
    "seminar",
    "networking",
    "social",
    "sports",
    "cultural",
    "educational",
    "other",
]

# Sample organizations
ORGANIZATIONS = [
    "Tech Meetup Group",
    "Python Society",
    "MongoDB Community",
    "Web Developers United",
    "Data Science Club",
    "AI Research Group",
    "Startup Network",
    "Creative Agency",
    "University Club",
    "Professional Association",
    "Local Community Center",
]

# Common tech tags
TECH_TAGS = [
    "python",
    "mongodb",
    "javascript",
    "react",
    "nodejs",
    "AI",
    "ML",
    "data-science",
    "web-dev",
    "mobile",
    "cloud",
    "devops",
    "blockchain",
    "cybersecurity",
    "startup",
    "networking",
    "career",
    "freelance",
]


def generate_coordinates():
    """Generate realistic coordinates (focused on major cities)"""
    cities = [
        (40.7128, -74.0060),  # New York
        (34.0522, -118.2437),  # Los Angeles
        (41.8781, -87.6298),  # Chicago
        (29.7604, -95.3698),  # Houston
        (33.4484, -112.0740),  # Phoenix
        (39.7392, -104.9903),  # Denver
        (47.6062, -122.3321),  # Seattle
        (37.7749, -122.4194),  # San Francisco
        (25.7617, -80.1918),  # Miami
        (42.3601, -71.0589),  # Boston
    ]

    # Select a random city and add some random offset
    base_lat, base_lng = random.choice(cities)
    lat_offset = random.uniform(-0.5, 0.5)  # About 50km max offset
    lng_offset = random.uniform(-0.5, 0.5)

    return [base_lng + lng_offset, base_lat + lat_offset]


def generate_event_data():
    """Generate fake event data"""
    start_date = fake.date_time_between(start_date="-30d", end_date="+90d")

    # 30% chance of having an end date
    end_date = None
    if random.random() < 0.3:
        end_date = start_date + timedelta(
            hours=random.randint(1, 8), minutes=random.randint(0, 59)
        )

    # Generate relevant title based on category
    category = random.choice(CATEGORIES)

    if category == "conference":
        title = fake.catch_phrase() + " Conference"
    elif category == "workshop":
        title = fake.catch_phrase() + " Workshop"
    elif category == "meetup":
        title = fake.company() + " Meetup"
    else:
        title = fake.catch_phrase() + " " + category.title()

    # Generate tags
    num_tags = random.randint(1, 5)
    tags = random.sample(TECH_TAGS, min(num_tags, len(TECH_TAGS)))

    return {
        "title": title[:200],  # Ensure within length limit
        "description": fake.paragraph(nb_sentences=random.randint(2, 5))[:1000],
        "category": category,
        "location": {"type": "Point", "coordinates": generate_coordinates()},
        "start_date": start_date,
        "end_date": end_date,
        "organizer": random.choice(ORGANIZATIONS),
        "max_attendees": random.choice([None, 50, 100, 200, 500, 1000]),
        "tags": tags,
    }


def create_sample_events(count=50):
    """Create sample events in the database"""
    print(f"Creating {count} sample events...")

    # Connect to database
    db = get_mongodb()

    if not db.is_connected():
        print("Failed to connect to MongoDB!")
        return

    created_count = 0

    for i in range(count):
        try:
            event_data = generate_event_data()
            event_create = EventCreate(**event_data)
            event = get_event_service().create_event(event_create)

            created_count += 1

            if created_count % 10 == 0:
                print(f"Created {created_count} events...")

        except Exception as e:
            print(f"Error creating event {i+1}: {e}")
            continue

    print(f"\nSuccessfully created {created_count} events!")

    # Print some statistics
    categories = get_event_service().get_categories()
    print(f"Categories: {', '.join(categories)}")

    # Get total event count
    total_events = db.events.count_documents({})
    print(f"Total events in database: {total_events}")


def clear_all_events():
    """Clear all events from the database (use with caution!)"""
    response = input("Are you sure you want to delete ALL events? (yes/no): ")
    if response.lower() == "yes":
        db = get_mongodb()
        result = db.events.delete_many({})
        print(f"Deleted {result.deleted_count} events.")
    else:
        print("Operation cancelled.")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate sample event data")
    parser.add_argument(
        "--count", type=int, default=50, help="Number of events to create"
    )
    parser.add_argument(
        "--clear", action="store_true", help="Clear all existing events first"
    )

    args = parser.parse_args()

    if args.clear:
        clear_all_events()

    create_sample_events(args.count)


if __name__ == "__main__":
    main()
