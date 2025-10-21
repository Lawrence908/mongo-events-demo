// Basic CRUD Operations for Events Collection
// Student ID: 664 870 797 - Chris Lawrence
// CSCI 485 - Fall 2025

print("=".repeat(60));
print("EVENTS COLLECTION - CRUD OPERATIONS");
print("=".repeat(60));

// ===== CREATE OPERATIONS =====
print("\n1. CREATE OPERATIONS");
print("-".repeat(30));

// Create a new in-person event
print("Creating a new in-person event...");
db.events.insertOne({
    title: "Vancouver Food Festival 2025",
    description: "Celebrate the diverse culinary landscape of Vancouver with local chefs and restaurants.",
    category: "Food & Drink",
    eventType: "inPerson",
    schemaVersion: "1.0",
    location: {
        type: "Point",
        coordinates: [-123.1207, 49.2827] // Vancouver downtown
    },
    venueId: ObjectId("68ddb640c00b1dff057fb3b4"), // Queen Elizabeth Park
    venueReference: {
        name: "Queen Elizabeth Park",
        city: "Vancouver",
        capacity: 5000,
        venueType: "park"
    },
    startDate: new Date("2025-07-15T11:00:00Z"),
    endDate: new Date("2025-07-15T20:00:00Z"),
    organizer: "Vancouver Culinary Society",
    maxAttendees: 2000,
    currentAttendees: 0,
    price: 45,
    currency: "CAD",
    isFree: false,
    status: "published",
    tags: ["food", "festival", "outdoor", "family-friendly", "local"],
    metadata: {
        ageRestriction: "All Ages",
        dressCode: "Casual",
        accessibilityFeatures: ["Wheelchair Accessible", "Family Restrooms"]
    },
    tickets: [
        {
            tier: "Early Bird",
            price: 35,
            available: 500,
            sold: 0
        },
        {
            tier: "General Admission",
            price: 45,
            available: 1500,
            sold: 0
        }
    ],
    computedStats: {
        totalTicketsSold: 0,
        totalRevenue: 0,
        attendanceRate: 0,
        reviewCount: 0,
        averageRating: 0,
        lastUpdated: new Date()
    },
    createdAt: new Date(),
    updatedAt: new Date()
});

// Create multiple events at once
print("Creating multiple events with insertMany...");
db.events.insertMany([
    {
        title: "AI Workshop Series - Session 1",
        description: "Introduction to Machine Learning fundamentals for beginners.",
        category: "Technology",
        eventType: "virtual",
        schemaVersion: "1.0",
        location: {
            type: "Point",
            coordinates: [-123.1207, 49.2827]
        },
        startDate: new Date("2025-11-20T19:00:00Z"),
        endDate: new Date("2025-11-20T21:00:00Z"),
        organizer: "Vancouver AI Society",
        maxAttendees: 100,
        currentAttendees: 0,
        price: 0,
        currency: "CAD",
        isFree: true,
        status: "published",
        tags: ["technology", "AI", "workshop", "beginner", "free"],
        virtualDetails: {
            platform: "Zoom",
            meetingUrl: "https://zoom.us/j/987654321",
            recordingAvailable: true,
            timezone: "PST"
        },
        tickets: [{
            tier: "Free Registration",
            price: 0,
            available: 100,
            sold: 0
        }],
        createdAt: new Date(),
        updatedAt: new Date()
    },
    {
        title: "Monthly Book Club Meeting",
        description: "Discussing 'The Seven Husbands of Evelyn Hugo' this month.",
        category: "Arts & Culture",
        eventType: "recurring",
        schemaVersion: "1.0",
        location: {
            type: "Point",
            coordinates: [-123.9351, 49.0831] // Nanaimo
        },
        startDate: new Date("2025-11-05T18:30:00Z"),
        endDate: new Date("2025-11-05T20:30:00Z"),
        organizer: "Nanaimo Public Library",
        maxAttendees: 25,
        currentAttendees: 0,
        price: 0,
        currency: "CAD",
        isFree: true,
        status: "published",
        tags: ["books", "discussion", "monthly", "community", "free"],
        recurringDetails: {
            frequency: "monthly",
            endRecurrence: new Date("2025-12-31T23:59:59Z"),
            exceptions: []
        },
        tickets: [{
            tier: "Free Attendance",
            price: 0,
            available: 25,
            sold: 0
        }],
        createdAt: new Date(),
        updatedAt: new Date()
    }
]);

// ===== READ OPERATIONS =====
print("\n2. READ OPERATIONS");
print("-".repeat(30));

// Find all events
print("Finding all events (limited to 3):");
db.events.find().limit(3).forEach(event => {
    print(`- ${event.title} (${event.category}) - ${event.eventType}`);
});

// Find events by category
print("\nFinding Technology events:");
db.events.find({ category: "Technology" }).forEach(event => {
    print(`- ${event.title} - ${event.startDate}`);
});

// Find events by event type (polymorphic query)
print("\nFinding virtual events:");
db.events.find({ eventType: "virtual" }).forEach(event => {
    print(`- ${event.title} - Platform: ${event.virtualDetails?.platform || 'N/A'}`);
});

// Find free events
print("\nFinding free events:");
db.events.find({ isFree: true }).forEach(event => {
    print(`- ${event.title} - ${event.category}`);
});

// Find events in date range
print("\nFinding events in November 2025:");
db.events.find({
    startDate: {
        $gte: new Date("2025-11-01T00:00:00Z"),
        $lte: new Date("2025-11-30T23:59:59Z")
    }
}).forEach(event => {
    print(`- ${event.title} - ${event.startDate.toISOString().split('T')[0]}`);
});

// Find events with specific tags
print("\nFinding events tagged as 'workshop':");
db.events.find({ tags: "workshop" }).forEach(event => {
    print(`- ${event.title} - ${event.tags.join(', ')}`);
});

// Find events by venue type (Extended Reference Pattern)
print("\nFinding events at parks:");
db.events.find({ "venueReference.venueType": "park" }).forEach(event => {
    print(`- ${event.title} at ${event.venueReference.name}`);
});

// Complex query with multiple conditions
print("\nFinding published events under $50 in Vancouver area:");
db.events.find({
    status: "published",
    price: { $lt: 50 },
    "location.coordinates.0": { $gte: -123.5, $lte: -123.0 }, // Longitude range for Vancouver
    "location.coordinates.1": { $gte: 49.0, $lte: 49.5 }      // Latitude range for Vancouver
}).forEach(event => {
    print(`- ${event.title} - $${event.price} CAD`);
});

// ===== UPDATE OPERATIONS =====
print("\n3. UPDATE OPERATIONS");
print("-".repeat(30));

// Update a single event
print("Updating event status and attendee count...");
const updateResult = db.events.updateOne(
    { title: "Vancouver Food Festival 2025" },
    { 
        $set: { 
            currentAttendees: 150,
            "computedStats.totalTicketsSold": 150,
            "computedStats.totalRevenue": 6750,
            "computedStats.attendanceRate": 7.5,
            updatedAt: new Date()
        }
    }
);
print(`Updated ${updateResult.modifiedCount} document(s)`);

// Update multiple events
print("Updating all virtual events to include recording notice...");
const multiUpdateResult = db.events.updateMany(
    { eventType: "virtual" },
    { 
        $set: { 
            "virtualDetails.recordingNotice": "This session will be recorded for educational purposes",
            updatedAt: new Date()
        }
    }
);
print(`Updated ${multiUpdateResult.modifiedCount} document(s)`);

// Update using array operators
print("Adding a new tag to Technology events...");
db.events.updateMany(
    { category: "Technology" },
    { 
        $addToSet: { tags: "innovation" },
        $set: { updatedAt: new Date() }
    }
);

// Update embedded document (ticket pricing)
print("Updating ticket pricing for Food Festival...");
db.events.updateOne(
    { title: "Vancouver Food Festival 2025" },
    {
        $set: {
            "tickets.0.sold": 250,
            "tickets.0.available": 250,
            "tickets.1.sold": 100,
            "tickets.1.available": 1400,
            updatedAt: new Date()
        }
    }
);

// Upsert operation (update or insert)
print("Upserting an event (will create if doesn't exist)...");
db.events.updateOne(
    { title: "Community Yoga in the Park" },
    {
        $set: {
            title: "Community Yoga in the Park",
            description: "Free outdoor yoga session for all skill levels.",
            category: "Health & Wellness",
            eventType: "inPerson",
            schemaVersion: "1.0",
            location: {
                type: "Point",
                coordinates: [-123.1139, 49.2404]
            },
            startDate: new Date("2025-12-01T08:00:00Z"),
            endDate: new Date("2025-12-01T09:30:00Z"),
            organizer: "Vancouver Wellness Community",
            price: 0,
            isFree: true,
            status: "published",
            tags: ["yoga", "wellness", "outdoor", "free", "community"],
            createdAt: new Date(),
            updatedAt: new Date()
        }
    },
    { upsert: true }
);

// ===== DELETE OPERATIONS =====
print("\n4. DELETE OPERATIONS");
print("-".repeat(30));

// Delete a single event
print("Deleting a cancelled event...");
const deleteResult = db.events.deleteOne({
    title: "Community Yoga in the Park"
});
print(`Deleted ${deleteResult.deletedCount} document(s)`);

// Delete multiple events (be careful with this!)
print("Deleting all draft events...");
const multiDeleteResult = db.events.deleteMany({
    status: "draft"
});
print(`Deleted ${multiDeleteResult.deletedCount} document(s)`);

// Conditional delete with date criteria
print("Deleting completed events older than 6 months...");
const sixMonthsAgo = new Date();
sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);

const oldEventsResult = db.events.deleteMany({
    status: "completed",
    endDate: { $lt: sixMonthsAgo }
});
print(`Deleted ${oldEventsResult.deletedCount} old completed event(s)`);

// ===== ADVANCED CRUD OPERATIONS =====
print("\n5. ADVANCED CRUD OPERATIONS");
print("-".repeat(30));

// Find and modify (atomic operation)
print("Finding and updating event with atomic operation...");
const findAndModifyResult = db.events.findOneAndUpdate(
    { category: "Technology", status: "published" },
    { 
        $inc: { currentAttendees: 1 },
        $set: { updatedAt: new Date() }
    },
    { returnDocument: "after" }
);
if (findAndModifyResult) {
    print(`Updated event: ${findAndModifyResult.title} - New attendee count: ${findAndModifyResult.currentAttendees}`);
}

// Bulk operations
print("Performing bulk write operations...");
const bulkOps = [
    {
        updateOne: {
            filter: { eventType: "hybrid" },
            update: { $set: { "hybridDetails.streamingQuality": "HD" } }
        }
    },
    {
        updateMany: {
            filter: { category: "Music" },
            update: { $addToSet: { tags: "live-performance" } }
        }
    },
    {
        insertOne: {
            document: {
                title: "Test Event for Bulk Insert",
                category: "Test",
                eventType: "inPerson",
                schemaVersion: "1.0",
                location: { type: "Point", coordinates: [-123.1207, 49.2827] },
                startDate: new Date("2025-12-31T23:59:59Z"),
                createdAt: new Date(),
                updatedAt: new Date()
            }
        }
    }
];

const bulkResult = db.events.bulkWrite(bulkOps);
print(`Bulk operations completed: ${bulkResult.modifiedCount} modified, ${bulkResult.insertedCount} inserted`);

// Clean up test event
db.events.deleteOne({ title: "Test Event for Bulk Insert" });

print("\nCRUD Operations completed successfully!");
print("=".repeat(60));
