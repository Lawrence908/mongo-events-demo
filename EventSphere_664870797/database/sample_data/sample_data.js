// Sample Data for EventSphere - Demonstration Dataset
// Student ID: 664 870 797 - Chris Lawrence
// CSCI 485 - Fall 2025

print("Loading sample data for EventSphere...");

// ===== EVENTS SAMPLE DATA =====
print("Inserting sample events...");

db.events.insertMany([
    {
        _id: ObjectId("68ddb640c00b1dff057fbefc"),
        title: "Tech Innovation Summit 2025",
        description: "Experience cutting-edge technology and network with industry leaders in a collaborative environment.",
        category: "Technology",
        eventType: "hybrid",
        schemaVersion: "1.0",
        location: {
            type: "Point",
            coordinates: [-123.93446771957665, 49.10036536726016], // Vancouver area
        },
        venueId: null,
        venueReference: null,
        startDate: ISODate("2025-10-09T18:37:26.047Z"),
        endDate: ISODate("2025-10-09T22:37:26.047Z"),
        organizer: "Tech Vancouver",
        maxAttendees: 500,
        currentAttendees: 125,
        price: 135,
        currency: "CAD",
        isFree: false,
        status: "published",
        tags: ["technology", "networking", "innovation", "professional", "hybrid"],
        hybridDetails: {
            virtualCapacity: 300,
            inPersonCapacity: 200,
            virtualMeetingUrl: "https://teams.microsoft.com/j/321999401",
        },
        metadata: {
            ageRestriction: "18+",
            dressCode: "Business Casual",
            accessibilityFeatures: ["Wheelchair Accessible", "Sign Language Interpreter"],
        },
        computedStats: {
            totalTicketsSold: 125,
            totalRevenue: 16875,
            attendanceRate: 25.0,
            reviewCount: 8,
            averageRating: 4.3,
            lastUpdated: ISODate("2025-10-01T23:16:16.047Z"),
        },
        tickets: [
            {
                tier: "Early Bird",
                price: 99,
                available: 25,
                sold: 75
            },
            {
                tier: "General Admission",
                price: 135,
                available: 325,
                sold: 50
            }
        ],
        createdAt: ISODate("2025-09-22T18:37:26.047Z"),
        updatedAt: ISODate("2025-09-22T18:37:26.047Z")
    },
    {
        _id: ObjectId("68ddb640c00b1dff057fbe02"),
        title: "Weekly Jazz Sessions",
        description: "Join us every Wednesday for intimate jazz performances featuring local and touring musicians.",
        category: "Music",
        eventType: "recurring",
        schemaVersion: "1.0",
        location: {
            type: "Point",
            coordinates: [-123.94587590269735, 49.06591877134164], // Nanaimo area
        },
        venueId: ObjectId("68ddb63fc00b1dff057fb35f"),
        venueReference: {
            name: "Blue Note Cafe - Nanaimo",
            city: "Nanaimo",
            capacity: 80,
            venueType: "restaurant",
        },
        startDate: ISODate("2025-10-16T19:00:00.000Z"),
        endDate: ISODate("2025-10-16T22:00:00.000Z"),
        organizer: "Nanaimo Jazz Society",
        maxAttendees: 80,
        currentAttendees: 45,
        price: 25,
        currency: "CAD",
        isFree: false,
        status: "published",
        tags: ["music", "jazz", "weekly", "intimate", "local"],
        recurringDetails: {
            frequency: "weekly",
            endRecurrence: ISODate("2025-12-31T23:59:59.000Z"),
            exceptions: [ISODate("2025-12-25T19:00:00.000Z")] // Christmas exception
        },
        metadata: {
            ageRestriction: "All Ages",
            dressCode: null,
            accessibilityFeatures: ["Wheelchair Accessible"],
        },
        computedStats: {
            totalTicketsSold: 45,
            totalRevenue: 1125,
            attendanceRate: 56.25,
            reviewCount: 12,
            averageRating: 4.7,
            lastUpdated: ISODate("2025-10-01T23:16:16.040Z"),
        },
        tickets: [
            {
                tier: "General Admission",
                price: 25,
                available: 35,
                sold: 45
            }
        ],
        createdAt: ISODate("2025-08-18T05:40:23.040Z"),
        updatedAt: ISODate("2025-08-16T05:40:23.040Z")
    },
    {
        _id: ObjectId("68ddb640c00b1dff057fbe03"),
        title: "Virtual Startup Pitch Competition",
        description: "Watch emerging startups pitch their innovative ideas to a panel of expert investors.",
        category: "Business",
        eventType: "virtual",
        schemaVersion: "1.0",
        location: {
            type: "Point",
            coordinates: [-123.1207, 49.2827], // Vancouver downtown
        },
        venueId: null,
        venueReference: null,
        startDate: ISODate("2025-11-15T18:00:00.000Z"),
        endDate: ISODate("2025-11-15T21:00:00.000Z"),
        organizer: "Vancouver Startup Hub",
        maxAttendees: 1000,
        currentAttendees: 234,
        price: 0,
        currency: "CAD",
        isFree: true,
        status: "published",
        tags: ["business", "startup", "virtual", "competition", "free"],
        virtualDetails: {
            platform: "Zoom",
            meetingUrl: "https://zoom.us/j/123456789",
            recordingAvailable: true,
            timezone: "PST"
        },
        metadata: {
            ageRestriction: "18+",
            dressCode: null,
            accessibilityFeatures: ["Live Captioning", "Audio Description"],
        },
        computedStats: {
            totalTicketsSold: 234,
            totalRevenue: 0,
            attendanceRate: 23.4,
            reviewCount: 5,
            averageRating: 4.1,
            lastUpdated: ISODate("2025-10-01T23:16:16.040Z"),
        },
        tickets: [
            {
                tier: "Free Registration",
                price: 0,
                available: 766,
                sold: 234
            }
        ],
        createdAt: ISODate("2025-09-01T10:00:00.000Z"),
        updatedAt: ISODate("2025-09-15T14:30:00.000Z")
    }
]);

// ===== VENUES SAMPLE DATA =====
print("Inserting sample venues...");

db.venues.insertMany([
    {
        _id: ObjectId("68ddb63fc00b1dff057fb398"),
        name: "Vancouver Convention Centre - West",
        venueType: "conferenceCenter",
        schemaVersion: "1.0",
        type: "Conference Center",
        description: "Premier waterfront convention center in downtown Vancouver with stunning harbor views.",
        location: {
            type: "Point",
            coordinates: [-123.1207, 49.2827],
        },
        address: {
            street: "1055 Canada Pl",
            city: "Vancouver",
            state: "BC",
            zipCode: "V6C 0C3",
            country: "Canada",
        },
        capacity: 2500,
        amenities: [
            "WiFi", "Parking", "Audio/Visual Equipment", "Catering",
            "Air Conditioning", "Accessibility", "Security", "Reception Area"
        ],
        contact: {
            phone: "(604) 689-8232",
            email: "info@vancouverconventioncentre.com",
            website: "https://www.vancouverconventioncentre.com",
        },
        pricing: { 
            hourlyRate: 500, 
            dailyRate: 3500, 
            currency: "CAD" 
        },
        availability: {
            monday: { open: "08:00", close: "22:00" },
            tuesday: { open: "08:00", close: "22:00" },
            wednesday: { open: "08:00", close: "22:00" },
            thursday: { open: "08:00", close: "22:00" },
            friday: { open: "08:00", close: "23:00" },
            saturday: { open: "09:00", close: "23:00" },
            sunday: { open: "09:00", close: "20:00" }
        },
        rating: 4.6,
        reviewCount: 89,
        conferenceCenterDetails: {
            breakoutRooms: 25,
            avEquipment: ["Video Conferencing", "Projectors", "Sound System", "Lighting"],
            cateringAvailable: true
        },
        computedStats: {
            totalEventsHosted: 156,
            averageAttendance: 850,
            revenueGenerated: 2450000,
            lastEventDate: ISODate("2025-09-28T23:16:15.999Z"),
            lastUpdated: ISODate("2025-10-01T23:16:15.999Z"),
        },
        createdAt: ISODate("2020-01-15T23:16:15.999Z"),
        updatedAt: ISODate("2025-09-20T23:16:15.999Z")
    },
    {
        _id: ObjectId("68ddb640c00b1dff057fb3b4"),
        name: "Queen Elizabeth Park",
        venueType: "park",
        schemaVersion: "1.0",
        type: "Park",
        description: "Beautiful 130-acre park with gardens, sports facilities, and stunning city views.",
        location: {
            type: "Point",
            coordinates: [-123.1139, 49.2404],
        },
        address: {
            street: "4600 Cambie St",
            city: "Vancouver",
            state: "BC",
            zipCode: "V5Z 2Z1",
            country: "Canada",
        },
        capacity: 5000,
        amenities: [
            "Parking", "Restrooms", "Outdoor Space", "Gardens",
            "Sports Facilities", "Accessibility", "Security"
        ],
        contact: {
            phone: "(604) 873-7000",
            email: "parks@vancouver.ca",
            website: "https://vancouver.ca/parks-recreation-culture/queen-elizabeth-park.aspx",
        },
        pricing: { 
            hourlyRate: 150, 
            dailyRate: 800, 
            currency: "CAD" 
        },
        availability: {
            monday: { open: "06:00", close: "22:00" },
            tuesday: { open: "06:00", close: "22:00" },
            wednesday: { open: "06:00", close: "22:00" },
            thursday: { open: "06:00", close: "22:00" },
            friday: { open: "06:00", close: "22:00" },
            saturday: { open: "06:00", close: "22:00" },
            sunday: { open: "06:00", close: "22:00" }
        },
        rating: 4.4,
        reviewCount: 234,
        parkDetails: {
            outdoorSpace: true,
            parkingSpaces: 200,
            restroomFacilities: true
        },
        computedStats: {
            totalEventsHosted: 78,
            averageAttendance: 450,
            revenueGenerated: 125000,
            lastEventDate: ISODate("2025-09-15T23:16:16.000Z"),
            lastUpdated: ISODate("2025-10-01T23:16:16.000Z"),
        },
        createdAt: ISODate("2019-05-01T23:16:16.000Z"),
        updatedAt: ISODate("2025-09-12T23:16:16.000Z")
    }
]);

// ===== USERS SAMPLE DATA =====
print("Inserting sample users...");

db.users.insertMany([
    {
        _id: ObjectId("68ddb640c00b1dff057fb511"),
        email: "sarah.johnson@gmail.com",
        schemaVersion: "1.0",
        profile: {
            firstName: "Sarah",
            lastName: "Johnson",
            preferences: {
                categories: ["Technology", "Business", "Networking", "Education"],
                location: {
                    type: "Point",
                    coordinates: [-123.1207, 49.2827], // Vancouver
                },
                radiusKm: 25
            }
        },
        createdAt: ISODate("2024-03-15T10:30:00.000Z"),
        updatedAt: ISODate("2025-09-20T14:22:00.000Z"),
        lastLogin: ISODate("2025-10-01T09:15:00.000Z")
    },
    {
        _id: ObjectId("68ddb640c00b1dff057fb51e"),
        email: "mike.chen@outlook.com",
        schemaVersion: "1.0",
        profile: {
            firstName: "Mike",
            lastName: "Chen",
            preferences: {
                categories: ["Music", "Arts & Culture", "Entertainment", "Food & Drink"],
                location: {
                    type: "Point",
                    coordinates: [-123.9351, 49.0831], // Nanaimo
                },
                radiusKm: 50
            }
        },
        createdAt: ISODate("2024-07-22T16:45:00.000Z"),
        updatedAt: ISODate("2025-08-10T11:30:00.000Z"),
        lastLogin: ISODate("2025-09-28T20:45:00.000Z")
    }
]);

// ===== REVIEWS SAMPLE DATA =====
print("Inserting sample reviews...");

db.reviews.insertMany([
    {
        _id: ObjectId("68ddb640c00b1dff057ff76a"),
        eventId: ObjectId("68ddb640c00b1dff057fbefc"),
        userId: ObjectId("68ddb640c00b1dff057fb511"),
        rating: 5,
        comment: "Outstanding tech summit! The hybrid format worked perfectly and the speakers were world-class. Great networking opportunities both in-person and virtual.",
        schemaVersion: "1.0",
        createdAt: ISODate("2025-10-10T14:30:00.000Z"),
        updatedAt: null
    },
    {
        _id: ObjectId("68ddb640c00b1dff057ff771"),
        eventId: ObjectId("68ddb640c00b1dff057fbe02"),
        userId: ObjectId("68ddb640c00b1dff057fb51e"),
        rating: 5,
        comment: "Amazing jazz session! The intimate venue and talented musicians created a perfect evening. Will definitely be back next week.",
        schemaVersion: "1.0",
        createdAt: ISODate("2025-10-17T23:15:00.000Z"),
        updatedAt: null
    },
    {
        _id: ObjectId("68ddb640c00b1dff057ff772"),
        venueId: ObjectId("68ddb63fc00b1dff057fb398"),
        userId: ObjectId("68ddb640c00b1dff057fb511"),
        rating: 4,
        comment: "Excellent convention center with great facilities and stunning harbor views. Professional staff and top-notch AV equipment.",
        schemaVersion: "1.0",
        createdAt: ISODate("2025-09-29T16:20:00.000Z"),
        updatedAt: null
    }
]);

// ===== CHECKINS SAMPLE DATA =====
print("Inserting sample checkins...");

db.checkins.insertMany([
    {
        _id: ObjectId("68ddb640c00b1dff05809406"),
        eventId: ObjectId("68ddb640c00b1dff057fbefc"),
        userId: ObjectId("68ddb640c00b1dff057fb511"),
        venueId: ObjectId("68ddb63fc00b1dff057fb398"),
        checkInTime: ISODate("2025-10-09T18:15:00.000Z"),
        qrCode: "QR-TECH2025-001",
        schemaVersion: "1.0",
        ticketTier: "Early Bird",
        checkInMethod: "qrCode",
        location: {
            type: "Point",
            coordinates: [-123.1207, 49.2827],
        },
        metadata: {
            deviceInfo: "iPhone 15 Pro",
            ipAddress: "192.168.1.100",
            staffVerified: true
        },
        createdAt: ISODate("2025-10-09T18:15:00.000Z"),
        updatedAt: ISODate("2025-10-09T18:15:00.000Z")
    },
    {
        _id: ObjectId("68ddb640c00b1dff05809432"),
        eventId: ObjectId("68ddb640c00b1dff057fbe02"),
        userId: ObjectId("68ddb640c00b1dff057fb51e"),
        venueId: ObjectId("68ddb63fc00b1dff057fb35f"),
        checkInTime: ISODate("2025-10-16T18:45:00.000Z"),
        qrCode: "QR-JAZZ-WED-001",
        schemaVersion: "1.0",
        ticketTier: "General Admission",
        checkInMethod: "mobileApp",
        location: {
            type: "Point",
            coordinates: [-123.94587590269735, 49.06591877134164],
        },
        metadata: {
            deviceInfo: "Samsung Galaxy S24",
            ipAddress: "10.0.0.25",
            staffVerified: false
        },
        createdAt: ISODate("2025-10-16T18:45:00.000Z"),
        updatedAt: ISODate("2025-10-16T18:45:00.000Z")
    }
]);

print("\nSample data loaded successfully!");
print("=".repeat(50));
print("SAMPLE DATA SUMMARY:");
print("=".repeat(50));
print("Events: 3 (hybrid, recurring, virtual)");
print("Venues: 2 (conference center, park)");
print("Users: 2 (with preferences and locations)");
print("Reviews: 3 (events and venues)");
print("Check-ins: 2 (different methods and devices)");
print("=".repeat(50));
print("Features Demonstrated:");
print("• Polymorphic event types (hybrid, recurring, virtual)");
print("• Polymorphic venue types (conferenceCenter, park)");
print("• Geospatial data (Vancouver and Nanaimo locations)");
print("• Extended reference pattern (venue data in events)");
print("• Computed pattern (pre-calculated statistics)");
print("• Schema versioning (all documents v1.0)");
print("• Bridge collection pattern (checkins)");
print("=".repeat(50));
print("Ready for query demonstrations and testing!");
