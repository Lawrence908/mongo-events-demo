// Clean sample data for direct MongoDB insertion
// This version uses the updated sample data from sample_data.js with proper validation

// Events
db.events.insertMany([
    {
        "title": "Entertainment Event",
        "description": "Experience something new and exciting in a welcoming and inclusive atmosphere.",
        "category": "Entertainment",
        "event_type": "hybrid",
        "schemaVersion": "1.0",
        "location": {
            "type": "Point",
            "coordinates": [-123.93446771957665, 49.10036536726016]
        },
        "venueId": null, // Will be set to actual venue ID after venues are inserted
        "venue_reference": null,
        "start_date": new Date("2025-10-09T18:37:26.047Z"),
        "end_date": new Date("2025-10-09T22:37:26.047Z"),
        "organizer": "Art Gallery",
        "max_attendees": 990,
        "current_attendees": 25,
        "price": 135,
        "currency": "CAD",
        "is_free": false,
        "status": "cancelled",
        "tags": ["creative", "networking", "adults-only", "outdoor", "educational"],
        "created_at": new Date("2025-09-22T18:37:26.047Z"),
        "updated_at": new Date("2025-09-22T18:37:26.047Z"),
        "hybrid_details": {
            "virtual_capacity": 877,
            "in_person_capacity": 50,
            "virtual_meeting_url": "https://teams.microsoft.com/j/321999401"
        },
        "metadata": {
            "age_restriction": "21+",
            "dress_code": null,
            "accessibility_features": []
        },
        "computed_stats": {
            "total_tickets_sold": 945,
            "total_revenue": 127575,
            "attendance_rate": 95.45,
            "review_count": 39,
            "average_rating": 4.1,
            "last_updated": new Date("2025-10-01T23:16:16.047Z")
        },
        "tickets": [
            {
                "tier": "General Admission",
                "price": 135,
                "available": 115,
                "sold": 51
            }
        ]
    },
    {
        "title": "Entertainment Event",
        "description": "A unique experience that brings together like-minded individuals in a collaborative environment.",
        "category": "Entertainment",
        "event_type": "recurring",
        "schemaVersion": "1.0",
        "location": {
            "type": "Point",
            "coordinates": [-123.94587590269735, 49.06591877134164]
        },
        "venueId": null, // Will be set to actual venue ID after venues are inserted
        "venue_reference": {
            "name": "Remote Gathering Space - Nanaimo",
            "city": "Nanaimo",
            "capacity": 5823,
            "venue_type": "virtual_space"
        },
        "start_date": new Date("2025-09-07T05:40:23.040Z"),
        "end_date": new Date("2025-09-07T08:40:23.040Z"),
        "organizer": "Conference Center",
        "max_attendees": null,
        "current_attendees": 28,
        "price": 181,
        "currency": "CAD",
        "is_free": false,
        "status": "completed",
        "tags": ["creative", "adults-only", "educational", "free", "interactive"],
        "created_at": new Date("2025-08-18T05:40:23.040Z"),
        "updated_at": new Date("2025-08-16T05:40:23.040Z"),
        "recurring_details": {
            "frequency": "daily",
            "end_recurrence": new Date("2025-11-25T05:40:23.040Z"),
            "exceptions": [new Date("2025-09-17T05:40:23.040Z")]
        },
        "metadata": {
            "age_restriction": "All Ages",
            "dress_code": null,
            "accessibility_features": []
        },
        "computed_stats": {
            "total_tickets_sold": 95,
            "total_revenue": 17195,
            "attendance_rate": 95.2,
            "review_count": 46,
            "average_rating": 4.1,
            "last_updated": new Date("2025-10-01T23:16:16.040Z")
        },
        "tickets": [
            {
                "tier": "General Admission",
                "price": 181,
                "available": 35,
                "sold": 38
            }
        ]
    }
]);

// Venues
db.venues.insertMany([
    {
        "name": "Business Center Plaza - Nanaimo",
        "venue_type": "conference_center",
        "schemaVersion": "1.0",
        "type": "Conference Center",
        "description": "A conference center located in Nanaimo, perfect for various events and gatherings.",
        "location": {
            "type": "Point",
            "coordinates": [-124.0050633506158, 49.082833644770226]
        },
        "address": {
            "street": "5744 Main St",
            "city": "Nanaimo",
            "state": "BC",
            "zip_code": "V9T 6N3",
            "country": "Canada"
        },
        "capacity": 596,
        "amenities": [
            "Heating",
            "Storage",
            "Audio/Visual Equipment",
            "Catering",
            "Balcony",
            "Bar",
            "Dressing Rooms"
        ],
        "contact": {
            "phone": "(906) 231-6324",
            "email": "info@businesscenterplaza.com",
            "website": "https://www.businesscenterplaza.com"
        },
        "pricing": {
            "hourly_rate": 146,
            "daily_rate": 342,
            "currency": "CAD"
        },
        "availability": {
            "monday": { "open": "09:00", "close": "22:00" },
            "tuesday": { "open": "09:00", "close": "22:00" },
            "wednesday": { "open": "09:00", "close": "22:00" },
            "thursday": { "open": "09:00", "close": "22:00" },
            "friday": { "open": "09:00", "close": "23:00" },
            "saturday": { "open": "10:00", "close": "23:00" },
            "sunday": { "open": "10:00", "close": "20:00" }
        },
        "rating": 4.2,
        "review_count": 17,
        "created_at": new Date("2024-12-28T23:16:15.999Z"),
        "updated_at": new Date("2025-09-20T23:16:15.999Z"),
        "conference_center_details": {
            "breakout_rooms": 12,
            "a_v_equipment": [
                "Video Conferencing",
                "Projectors",
                "Whiteboards",
                "Sound System"
            ],
            "catering_available": false
        },
        "computed_stats": {
            "total_events_hosted": 70,
            "average_attendance": 478,
            "revenue_generated": 41490,
            "last_event_date": new Date("2025-09-13T23:16:15.999Z"),
            "last_updated": new Date("2025-10-01T23:16:15.999Z")
        }
    },
    {
        "name": "City Park - Nanaimo",
        "venue_type": "park",
        "schemaVersion": "1.0",
        "type": "Park",
        "description": "A park located in Nanaimo, perfect for various events and gatherings.",
        "location": {
            "type": "Point",
            "coordinates": [-123.87792727192632, 49.05384388261788]
        },
        "address": {
            "street": "1419 Elm St",
            "city": "Nanaimo",
            "state": "BC",
            "zip_code": "V9T 6N3",
            "country": "Canada"
        },
        "capacity": 4406,
        "amenities": [
            "Audio/Visual Equipment",
            "Air Conditioning",
            "Reception Area",
            "Catering",
            "Balcony",
            "Parking",
            "Security"
        ],
        "contact": {
            "phone": "(727) 445-7006",
            "email": "info@citypark.com",
            "website": "https://www.citypark.com"
        },
        "pricing": {
            "hourly_rate": 135,
            "daily_rate": 1112,
            "currency": "CAD"
        },
        "availability": {
            "monday": { "open": "09:00", "close": "22:00" },
            "tuesday": { "open": "09:00", "close": "22:00" },
            "wednesday": { "open": "09:00", "close": "22:00" },
            "thursday": { "open": "09:00", "close": "22:00" },
            "friday": { "open": "09:00", "close": "23:00" },
            "saturday": { "open": "10:00", "close": "23:00" },
            "sunday": { "open": "10:00", "close": "20:00" }
        },
        "rating": 3.2,
        "review_count": 63,
        "created_at": new Date("2024-12-12T23:16:16.000Z"),
        "updated_at": new Date("2025-09-12T23:16:16.000Z"),
        "park_details": {
            "outdoor_space": true,
            "parking_spaces": 238,
            "restroom_facilities": true
        },
        "computed_stats": {
            "total_events_hosted": 53,
            "average_attendance": 97,
            "revenue_generated": 36100,
            "last_event_date": new Date("2025-08-19T23:16:16.000Z"),
            "last_updated": new Date("2025-10-01T23:16:16.000Z")
        }
    }
]);

// Users
db.users.insertMany([
    {
        "email": "barbara.williams@yahoo.com",
        "schemaVersion": "1.0",
        "profile": {
            "first_name": "Barbara",
            "last_name": "Williams",
            "preferences": {
                "categories": ["Fitness", "Politics", "Health & Wellness", "Meditation"],
                "location": {
                    "type": "Point",
                    "coordinates": [-80.48434831242973, 43.52343446108092]
                },
                "radius_km": 38
            }
        },
        "created_at": new Date("2025-04-09T23:16:16.008Z"),
        "updated_at": new Date("2025-04-09T23:16:16.008Z"),
        "last_login": new Date("2025-04-16T23:16:16.008Z")
    },
    {
        "email": "richard.davis@outlook.com",
        "schemaVersion": "1.0",
        "profile": {
            "first_name": "Richard",
            "last_name": "Davis",
            "preferences": {
                "categories": [
                    "Health & Wellness",
                    "Swimming",
                    "Music",
                    "Photography",
                    "Theater"
                ],
                "location": {
                    "type": "Point",
                    "coordinates": [-83.33081084065205, 40.17509883954208]
                },
                "radius_km": 39
            }
        },
        "created_at": new Date("2024-02-01T23:16:16.008Z"),
        "updated_at": new Date("2024-02-01T23:16:16.008Z"),
        "last_login": null
    }
]);

// Reviews (event and venue) - Insert after users and events are created
// We'll insert these after getting the actual IDs

// Check-ins (bridge demonstrates many:many) - Insert after all other collections
// We'll insert these after getting the actual IDs

// Update references after insertion
// Get the inserted IDs and update the references
var venueIds = db.venues.find({}, {_id: 1}).toArray();
var eventIds = db.events.find({}, {_id: 1}).toArray();
var userIds = db.users.find({}, {_id: 1}).toArray();

// Update events with venue references
db.events.updateMany(
  {"venue_reference.name": "Remote Gathering Space - Nanaimo"},
  {$set: {"venueId": venueIds[1]._id}} // Use second venue (City Park)
);

// Insert reviews with proper references
db.reviews.insertMany([
    {
        "event_id": eventIds[0]._id,
        "user_id": userIds[0]._id,
        "rating": 5,
        "comment": "This was one of the best events I've attended this year. Highly recommend to anyone interested in this topic.",
        "schemaVersion": "1.0",
        "created_at": new Date("2026-03-17T09:04:00.028Z"),
        "updated_at": null
    },
    {
        "event_id": eventIds[1]._id,
        "user_id": userIds[1]._id,
        "rating": 3,
        "comment": "This event was a waste of time. Poor organization and the speakers were not engaging at all.",
        "schemaVersion": "1.0",
        "created_at": new Date("2026-03-28T17:36:52.028Z"),
        "updated_at": null
    }
]);

// Insert check-ins with proper references
db.checkins.insertMany([
    {
        "event_id": eventIds[0]._id,
        "user_id": userIds[0]._id,
        "venue_id": venueIds[0]._id,
        "check_in_time": new Date("2025-12-17T16:23:09.091Z"),
        "qr_code": "QR-554361",
        "schemaVersion": "1.0",
        "ticket_tier": "VIP",
        "check_in_method": "manual",
        "location": {
            "type": "Point",
            "coordinates": [-121.88338526503668, 37.2974440040109]
        },
        "metadata": {
            "device_info": "iPhone",
            "ip_address": "112.24.5.114",
            "staff_verified": true
        },
        "created_at": new Date("2025-12-17T16:23:09.091Z")
    },
    {
        "event_id": eventIds[1]._id,
        "user_id": userIds[1]._id,
        "venue_id": venueIds[1]._id,
        "check_in_time": new Date("2026-02-24T08:20:35.348Z"),
        "qr_code": "QR-502727",
        "schemaVersion": "1.0",
        "ticket_tier": null,
        "check_in_method": "qr_code",
        "location": {
            "type": "Point",
            "coordinates": [-73.68308130512068, 40.60712176280241]
        },
        "metadata": {
            "device_info": "Web Browser",
            "ip_address": null,
            "staff_verified": true
        },
        "created_at": new Date("2026-02-24T08:20:35.348Z")
    }
]);

print("Sample data inserted successfully with proper references!");
