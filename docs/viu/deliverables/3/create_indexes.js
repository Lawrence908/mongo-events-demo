// Enhanced Index Creation Script for EventSphere - Deliverable 3
// This script creates comprehensive indexes optimized for performance and query patterns

print("Creating indexes for EventSphere database...");

// ============================================================================
// EVENTS COLLECTION INDEXES
// ============================================================================

print("Creating indexes for events collection...");

// 1. Geospatial index for event discovery (HIGH PRIORITY)
db.events.createIndex({ location: "2dsphere" }, { 
    name: "events_location_2dsphere",
    background: true 
});
print("✓ Created geospatial index for event discovery");

// 2. Text search across key fields (HIGH PRIORITY)
db.events.createIndex({ 
    title: "text", 
    description: "text", 
    category: "text", 
    tags: "text" 
}, { 
    name: "events_text_search",
    background: true,
    weights: { title: 10, category: 5, tags: 3, description: 1 }
});
print("✓ Created text search index with relevance weighting");

// 3. Date-based indexes for temporal queries (HIGH PRIORITY)
db.events.createIndex({ startDate: 1 }, { 
    name: "events_startDate_asc",
    background: true 
});
db.events.createIndex({ createdAt: 1 }, { 
    name: "events_createdAt_asc",
    background: true 
});
print("✓ Created date-based indexes for temporal queries");

// 4. Compound indexes for common filter combinations (HIGH PRIORITY)
db.events.createIndex({ category: 1, startDate: 1 }, { 
    name: "events_category_startDate",
    background: true 
});
db.events.createIndex({ organizer: 1, startDate: 1 }, { 
    name: "events_organizer_startDate",
    background: true 
});
print("✓ Created compound indexes for common filter combinations");

// 5. Polymorphic event type indexes (HIGH PRIORITY)
db.events.createIndex({ eventType: 1, startDate: 1 }, { 
    name: "events_eventType_startDate",
    background: true 
});
db.events.createIndex({ eventType: 1, category: 1 }, { 
    name: "events_eventType_category",
    background: true 
});
print("✓ Created polymorphic event type indexes");

// 6. Extended Reference Pattern indexes (MEDIUM PRIORITY)
db.events.createIndex({ "venueReference.venueType": 1, startDate: 1 }, { 
    name: "events_venueType_startDate",
    background: true 
});
db.events.createIndex({ "venueReference.city": 1, startDate: 1 }, { 
    name: "events_venueCity_startDate",
    background: true 
});
db.events.createIndex({ "venueReference.capacity": 1 }, { 
    name: "events_venueCapacity",
    background: true 
});
print("✓ Created extended reference pattern indexes");

// 7. Geospatial + Date compound index (HIGH PRIORITY)
db.events.createIndex({ location: "2dsphere", startDate: 1 }, { 
    name: "events_location_startDate",
    background: true 
});
print("✓ Created geospatial + date compound index");

// 8. Cursor-based pagination support (HIGH PRIORITY)
db.events.createIndex({ _id: 1, startDate: 1 }, { 
    name: "events_id_startDate_pagination",
    background: true 
});
print("✓ Created cursor-based pagination index");

// 9. Status and filtering indexes (MEDIUM PRIORITY)
db.events.createIndex({ status: 1, startDate: 1 }, { 
    name: "events_status_startDate",
    background: true 
});
db.events.createIndex({ isFree: 1, startDate: 1 }, { 
    name: "events_isFree_startDate",
    background: true 
});
print("✓ Created status and filtering indexes");

// 10. Schema versioning index (LOW PRIORITY)
db.events.createIndex({ schemaVersion: 1 }, { 
    name: "events_schemaVersion",
    background: true 
});
print("✓ Created schema versioning index");

// ============================================================================
// VENUES COLLECTION INDEXES
// ============================================================================

print("Creating indexes for venues collection...");

// 1. Geospatial index for venue discovery (HIGH PRIORITY)
db.venues.createIndex({ location: "2dsphere" }, { 
    name: "venues_location_2dsphere",
    background: true 
});
print("✓ Created geospatial index for venue discovery");

// 2. Polymorphic venue type indexes (HIGH PRIORITY)
db.venues.createIndex({ venueType: 1, capacity: 1 }, { 
    name: "venues_venueType_capacity",
    background: true 
});
db.venues.createIndex({ venueType: 1, rating: 1 }, { 
    name: "venues_venueType_rating",
    background: true 
});
print("✓ Created polymorphic venue type indexes");

// 3. Capacity and rating indexes (MEDIUM PRIORITY)
db.venues.createIndex({ capacity: 1 }, { 
    name: "venues_capacity",
    background: true 
});
db.venues.createIndex({ rating: 1 }, { 
    name: "venues_rating",
    background: true 
});
print("✓ Created capacity and rating indexes");

// 4. City-based filtering (MEDIUM PRIORITY)
db.venues.createIndex({ "address.city": 1, venueType: 1 }, { 
    name: "venues_city_venueType",
    background: true 
});
print("✓ Created city-based filtering index");

// 5. Schema versioning index (LOW PRIORITY)
db.venues.createIndex({ schemaVersion: 1 }, { 
    name: "venues_schemaVersion",
    background: true 
});
print("✓ Created schema versioning index");

// ============================================================================
// USERS COLLECTION INDEXES
// ============================================================================

print("Creating indexes for users collection...");

// 1. Email uniqueness index (HIGH PRIORITY)
db.users.createIndex({ email: 1 }, { 
    name: "users_email_unique",
    unique: true,
    background: true 
});
print("✓ Created unique email index");

// 2. User preferences location index (MEDIUM PRIORITY)
db.users.createIndex({ "profile.preferences.location": "2dsphere" }, { 
    name: "users_preferences_location",
    background: true,
    sparse: true 
});
print("✓ Created user preferences location index");

// 3. Schema versioning index (LOW PRIORITY)
db.users.createIndex({ schemaVersion: 1 }, { 
    name: "users_schemaVersion",
    background: true 
});
print("✓ Created schema versioning index");

// ============================================================================
// REVIEWS COLLECTION INDEXES
// ============================================================================

print("Creating indexes for reviews collection...");

// 1. Event and venue reference indexes (HIGH PRIORITY)
db.reviews.createIndex({ eventId: 1 }, { 
    name: "reviews_eventId",
    background: true,
    sparse: true 
});
db.reviews.createIndex({ venueId: 1 }, { 
    name: "reviews_venueId",
    background: true,
    sparse: true 
});
print("✓ Created event and venue reference indexes");

// 2. User reference index (HIGH PRIORITY)
db.reviews.createIndex({ userId: 1 }, { 
    name: "reviews_userId",
    background: true 
});
print("✓ Created user reference index");

// 3. Rating-based queries (MEDIUM PRIORITY)
db.reviews.createIndex({ rating: 1 }, { 
    name: "reviews_rating",
    background: true 
});
db.reviews.createIndex({ createdAt: 1 }, { 
    name: "reviews_createdAt",
    background: true 
});
print("✓ Created rating and temporal indexes");

// 4. Aggregation-optimized compound indexes (HIGH PRIORITY)
db.reviews.createIndex({ eventId: 1, rating: 1 }, { 
    name: "reviews_eventId_rating",
    background: true,
    sparse: true 
});
db.reviews.createIndex({ venueId: 1, rating: 1 }, { 
    name: "reviews_venueId_rating",
    background: true,
    sparse: true 
});
print("✓ Created aggregation-optimized compound indexes");

// 5. Schema versioning index (LOW PRIORITY)
db.reviews.createIndex({ schemaVersion: 1 }, { 
    name: "reviews_schemaVersion",
    background: true 
});
print("✓ Created schema versioning index");

// ============================================================================
// CHECKINS COLLECTION INDEXES
// ============================================================================

print("Creating indexes for checkins collection...");

// 1. Event and user reference indexes (HIGH PRIORITY)
db.checkins.createIndex({ eventId: 1 }, { 
    name: "checkins_eventId",
    background: true 
});
db.checkins.createIndex({ userId: 1 }, { 
    name: "checkins_userId",
    background: true 
});
print("✓ Created event and user reference indexes");

// 2. Venue reference index (HIGH PRIORITY)
db.checkins.createIndex({ venueId: 1 }, { 
    name: "checkins_venueId",
    background: true 
});
print("✓ Created venue reference index");

// 3. Temporal indexes (HIGH PRIORITY)
db.checkins.createIndex({ checkInTime: 1 }, { 
    name: "checkins_checkInTime",
    background: true 
});
print("✓ Created temporal index");

// 4. QR code lookup index (HIGH PRIORITY)
db.checkins.createIndex({ qrCode: 1 }, { 
    name: "checkins_qrCode",
    background: true 
});
print("✓ Created QR code lookup index");

// 5. Duplicate prevention unique index (HIGH PRIORITY)
db.checkins.createIndex({ eventId: 1, userId: 1 }, { 
    name: "checkins_eventId_userId_unique",
    unique: true,
    background: true 
});
print("✓ Created duplicate prevention unique index");

// 6. Analytics-optimized compound indexes (HIGH PRIORITY)
db.checkins.createIndex({ venueId: 1, checkInTime: 1 }, { 
    name: "checkins_venueId_checkInTime",
    background: true 
});
db.checkins.createIndex({ userId: 1, checkInTime: 1 }, { 
    name: "checkins_userId_checkInTime",
    background: true 
});
print("✓ Created analytics-optimized compound indexes");

// 7. Ticket tier and method indexes (MEDIUM PRIORITY)
db.checkins.createIndex({ ticketTier: 1 }, { 
    name: "checkins_ticketTier",
    background: true,
    sparse: true 
});
db.checkins.createIndex({ checkInMethod: 1 }, { 
    name: "checkins_checkInMethod",
    background: true,
    sparse: true 
});
print("✓ Created ticket tier and method indexes");

// 8. Schema versioning index (LOW PRIORITY)
db.checkins.createIndex({ schemaVersion: 1 }, { 
    name: "checkins_schemaVersion",
    background: true 
});
print("✓ Created schema versioning index");

// ============================================================================
// ADDITIONAL OPTIMIZATION INDEXES
// ============================================================================

print("Creating additional optimization indexes...");

// 1. Partial indexes for active events only
db.events.createIndex(
    { startDate: 1, category: 1 }, 
    { 
        name: "events_active_startDate_category",
        background: true,
        partialFilterExpression: { 
            status: { $in: ["published", "draft"] },
            startDate: { $gte: new Date() }
        }
    }
);
print("✓ Created partial index for active events");

// 2. Sparse index for events with venue references
db.events.createIndex(
    { venueId: 1, startDate: 1 }, 
    { 
        name: "events_venueId_startDate",
        background: true,
        sparse: true 
    }
);
print("✓ Created sparse index for events with venue references");

// 3. Compound index for high-priority event queries
db.events.createIndex(
    { status: 1, eventType: 1, startDate: 1 }, 
    { 
        name: "events_status_eventType_startDate",
        background: true 
    }
);
print("✓ Created compound index for high-priority event queries");

// 4. Index for venue capacity range queries
db.venues.createIndex(
    { capacity: 1, venueType: 1, rating: 1 }, 
    { 
        name: "venues_capacity_venueType_rating",
        background: true 
    }
);
print("✓ Created index for venue capacity range queries");

// ============================================================================
// INDEX STATISTICS AND VALIDATION
// ============================================================================

print("Validating index creation...");

// Get index statistics for all collections
const collections = ['events', 'venues', 'users', 'reviews', 'checkins'];

collections.forEach(collection => {
    const indexes = db[collection].getIndexes();
    print(`\n${collection.toUpperCase()} Collection Indexes (${indexes.length} total):`);
    indexes.forEach(index => {
        print(`  - ${index.name}: ${JSON.stringify(index.key)}`);
    });
});

// Check for any index creation errors
print("\nIndex creation completed successfully!");
print("All indexes have been created with background: true to avoid blocking operations.");

// ============================================================================
// PERFORMANCE MONITORING QUERIES
// ============================================================================

print("\nTo monitor index performance, use these queries:");
print("1. Check index usage: db.events.aggregate([{ $indexStats: {} }])");
print("2. Check slow queries: db.setProfilingLevel(2, { slowms: 100 })");
print("3. Analyze query plans: db.events.find({...}).explain('executionStats')");

print("\nIndex creation script completed successfully!");
