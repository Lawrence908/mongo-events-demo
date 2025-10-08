// Clean sample data for direct MongoDB insertion
// This version uses the updated sample data from sample_data.js with proper validation

// Events
db.events.insertMany([
    {
        "title": "Entertainment Event",
        "description": "Experience something new and exciting in a welcoming and inclusive atmosphere.",
        "category": "Entertainment",
        "eventType": "hybrid",
        "schemaVersion": "1.0",
        "location": {
            "type": "Point",
            "coordinates": [-123.93446771957665, 49.10036536726016]
        },
        "venueId": null, // Will be set to actual venue ID after venues are inserted
        "venueReference": null,
        "startDate": new Date("2025-10-09T18:37:26.047Z"),
        "endDate": new Date("2025-10-09T22:37:26.047Z"),
        "organizer": "Art Gallery",
        "maxAttendees": 990,
        "currentAttendees": 25,
        "price": 135,
        "currency": "CAD",
        "isFree": false,
        "status": "cancelled",
        "tags": ["creative", "networking", "adults-only", "outdoor", "educational"],
        "createdAt": new Date("2025-09-22T18:37:26.047Z"),
        "updatedAt": new Date("2025-09-22T18:37:26.047Z"),
        "hybridDetails": {
            "virtualCapacity": 877,
            "inPersonCapacity": 50,
            "virtualMeetingUrl": "https://teams.microsoft.com/j/321999401"
        },
        "metadata": {
            "ageRestriction": "21+",
            "dressCode": null,
            "accessibilityFeatures": []
        },
        "computedStats": {
            "totalTicketsSold": 945,
            "totalRevenue": 127575,
            "attendanceRate": 95.45,
            "reviewCount": 39,
            "averageRating": 4.1,
            "lastUpdated": new Date("2025-10-01T23:16:16.047Z")
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
        "eventType": "recurring",
        "schemaVersion": "1.0",
        "location": {
            "type": "Point",
            "coordinates": [-123.94587590269735, 49.06591877134164]
        },
        "venueId": null, // Will be set to actual venue ID after venues are inserted
        "venueReference": {
            "name": "Remote Gathering Space - Nanaimo",
            "city": "Nanaimo",
            "capacity": 5823,
            "venueType": "virtualSpace"
        },
        "startDate": new Date("2025-09-07T05:40:23.040Z"),
        "endDate": new Date("2025-09-07T08:40:23.040Z"),
        "organizer": "Conference Center",
        "maxAttendees": null,
        "currentAttendees": 28,
        "price": 181,
        "currency": "CAD",
        "isFree": false,
        "status": "completed",
        "tags": ["creative", "adults-only", "educational", "free", "interactive"],
        "createdAt": new Date("2025-08-18T05:40:23.040Z"),
        "updatedAt": new Date("2025-08-16T05:40:23.040Z"),
        "recurringDetails": {
            "frequency": "daily",
            "endRecurrence": new Date("2025-11-25T05:40:23.040Z"),
            "exceptions": [new Date("2025-09-17T05:40:23.040Z")]
        },
        "metadata": {
            "ageRestriction": "All Ages",
            "dressCode": null,
            "accessibilityFeatures": []
        },
        "computedStats": {
            "totalTicketsSold": 95,
            "totalRevenue": 17195,
            "attendanceRate": 95.2,
            "reviewCount": 46,
            "averageRating": 4.1,
            "lastUpdated": new Date("2025-10-01T23:16:16.040Z")
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
        "venueType": "conferenceCenter",
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
            "zipCode": "V9T 6N3",
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
            "hourlyRate": 146,
            "dailyRate": 342,
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
        "reviewCount": 17,
        "createdAt": new Date("2024-12-28T23:16:15.999Z"),
        "updatedAt": new Date("2025-09-20T23:16:15.999Z"),
        "conferenceCenterDetails": {
            "breakoutRooms": 12,
            "avEquipment": [
                "Video Conferencing",
                "Projectors",
                "Whiteboards",
                "Sound System"
            ],
            "cateringAvailable": false
        },
        "computedStats": {
            "totalEventsHosted": 70,
            "averageAttendance": 478,
            "revenueGenerated": 41490,
            "lastEventDate": new Date("2025-09-13T23:16:15.999Z"),
            "lastUpdated": new Date("2025-10-01T23:16:15.999Z")
        }
    },
    {
        "name": "City Park - Nanaimo",
        "venueType": "park",
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
            "zipCode": "V9T 6N3",
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
            "hourlyRate": 135,
            "dailyRate": 1112,
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
        "reviewCount": 63,
        "createdAt": new Date("2024-12-12T23:16:16.000Z"),
        "updatedAt": new Date("2025-09-12T23:16:16.000Z"),
        "parkDetails": {
            "outdoorSpace": true,
            "parkingSpaces": 238,
            "restroomFacilities": true
        },
        "computedStats": {
            "totalEventsHosted": 53,
            "averageAttendance": 97,
            "revenueGenerated": 36100,
            "lastEventDate": new Date("2025-08-19T23:16:16.000Z"),
            "lastUpdated": new Date("2025-10-01T23:16:16.000Z")
        }
    }
]);

// Users
db.users.insertMany([
    {
        "email": "barbara.williams@yahoo.com",
        "schemaVersion": "1.0",
        "profile": {
            "firstName": "Barbara",
            "lastName": "Williams",
            "preferences": {
                "categories": ["Fitness", "Politics", "Health & Wellness", "Meditation"],
                "location": {
                    "type": "Point",
                    "coordinates": [-80.48434831242973, 43.52343446108092]
                },
                "radiusKm": 38
            }
        },
        "createdAt": new Date("2025-04-09T23:16:16.008Z"),
        "updatedAt": new Date("2025-04-09T23:16:16.008Z"),
        "lastLogin": new Date("2025-04-16T23:16:16.008Z")
    },
    {
        "email": "richard.davis@outlook.com",
        "schemaVersion": "1.0",
        "profile": {
            "firstName": "Richard",
            "lastName": "Davis",
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
                "radiusKm": 39
            }
        },
        "createdAt": new Date("2024-02-01T23:16:16.008Z"),
        "updatedAt": new Date("2024-02-01T23:16:16.008Z"),
        "lastLogin": null
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
  {"venueReference.name": "Remote Gathering Space - Nanaimo"},
  {$set: {"venueId": venueIds[1]._id}} // Use second venue (City Park)
);

// Insert reviews with proper references
db.reviews.insertMany([
    {
        "eventId": eventIds[0]._id,
        "userId": userIds[0]._id,
        "rating": 5,
        "comment": "This was one of the best events I've attended this year. Highly recommend to anyone interested in this topic.",
        "schemaVersion": "1.0",
        "createdAt": new Date("2026-03-17T09:04:00.028Z"),
        "updatedAt": null
    },
    {
        "eventId": eventIds[1]._id,
        "userId": userIds[1]._id,
        "rating": 3,
        "comment": "This event was a waste of time. Poor organization and the speakers were not engaging at all.",
        "schemaVersion": "1.0",
        "createdAt": new Date("2026-03-28T17:36:52.028Z"),
        "updatedAt": null
    }
]);

// Insert check-ins with proper references
db.checkins.insertMany([
    {
        "eventId": eventIds[0]._id,
        "userId": userIds[0]._id,
        "venueId": venueIds[0]._id,
        "checkInTime": new Date("2025-12-17T16:23:09.091Z"),
        "qrCode": "QR-554361",
        "schemaVersion": "1.0",
        "ticketTier": "VIP",
        "checkInMethod": "manual",
        "location": {
            "type": "Point",
            "coordinates": [-121.88338526503668, 37.2974440040109]
        },
        "metadata": {
            "deviceInfo": "iPhone",
            "ipAddress": "112.24.5.114",
            "staffVerified": true
        },
        "createdAt": new Date("2025-12-17T16:23:09.091Z")
    },
    {
        "eventId": eventIds[1]._id,
        "userId": userIds[1]._id,
        "venueId": venueIds[1]._id,
        "checkInTime": new Date("2026-02-24T08:20:35.348Z"),
        "qrCode": "QR-502727",
        "schemaVersion": "1.0",
        "ticketTier": null,
        "checkInMethod": "qrCode",
        "location": {
            "type": "Point",
            "coordinates": [-73.68308130512068, 40.60712176280241]
        },
        "metadata": {
            "deviceInfo": "Web Browser",
            "ipAddress": null,
            "staffVerified": true
        },
        "createdAt": new Date("2026-02-24T08:20:35.348Z")
    }
]);

print("Sample data inserted successfully with proper references!");
