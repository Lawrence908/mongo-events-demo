// Create Indexes Script for EventSphere - Deliverable 3


// ============================================================================
// EVENTS COLLECTION INDEXES
// ============================================================================


// 1. Geospatial index for event discovery (HIGHEST PRIORITY)
db.events.createIndex({ location: "2dsphere" }, { 
    name: "events_location_2dsphere",
    background: true 
});

// 2. Text search across key fields (HIGHEST PRIORITY)
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

// 3. Category + Date compound index (HIGH PRIORITY)
db.events.createIndex({ category: 1, startDate: 1 }, { 
    name: "events_category_startDate",
    background: true 
});

// 4. Event Type + Date compound index (HIGH PRIORITY)
db.events.createIndex({ eventType: 1, startDate: 1 }, { 
    name: "events_eventType_startDate",
    background: true 
});

// ============================================================================
// VENUES COLLECTION INDEXES
// ============================================================================


// 1. Geospatial index for venue discovery (HIGHEST PRIORITY)
db.venues.createIndex({ location: "2dsphere" }, { 
    name: "venues_location_2dsphere",
    background: true 
});

// 2. Venue Type + Capacity compound index (HIGH PRIORITY)
db.venues.createIndex({ venueType: 1, capacity: 1 }, { 
    name: "venues_venueType_capacity",
    background: true 
});

// 3. Text search across venue fields (HIGH PRIORITY)
db.venues.createIndex({ 
    name: "text", 
    description: "text", 
    amenities: "text",
    "address.city": "text"
}, { 
    name: "venues_text_search",
    background: true,
    weights: { name: 10, "address.city": 5, amenities: 3, description: 1 }
});

// 4. Venue Type + Rating compound index (MEDIUM PRIORITY)
db.venues.createIndex({ venueType: 1, rating: 1 }, { 
    name: "venues_venueType_rating",
    background: true 
});


// ============================================================================
// REVIEWS COLLECTION INDEXES
// ============================================================================


// 1. Event ID index (HIGHEST PRIORITY)
db.reviews.createIndex({ eventId: 1 }, { 
    name: "reviews_eventId",
    background: true,
    sparse: true 
});

// 2. Venue ID index (HIGH PRIORITY)
db.reviews.createIndex({ venueId: 1 }, { 
    name: "reviews_venueId",
    background: true,
    sparse: true 
});

// 3. Event ID + Rating compound index (HIGH PRIORITY)
db.reviews.createIndex({ eventId: 1, rating: 1 }, { 
    name: "reviews_eventId_rating",
    background: true,
    sparse: true 
});

// 4. User ID index (MEDIUM PRIORITY)
db.reviews.createIndex({ userId: 1 }, { 
    name: "reviews_userId",
    background: true 
});

// ============================================================================
// CHECKINS COLLECTION INDEXES
// ============================================================================


// 1. Event ID + User ID compound unique index (HIGHEST PRIORITY)
db.checkins.createIndex({ eventId: 1, userId: 1 }, { 
    name: "checkins_eventId_userId_unique",
    unique: true,
    background: true 
});

// 2. Event ID index (HIGH PRIORITY)
db.checkins.createIndex({ eventId: 1 }, { 
    name: "checkins_eventId",
    background: true 
});

// 3. User ID index (HIGH PRIORITY)
db.checkins.createIndex({ userId: 1 }, { 
    name: "checkins_userId",
    background: true 
});

// 4. Venue ID + Check-in Time compound index (MEDIUM PRIORITY)
db.checkins.createIndex({ venueId: 1, checkInTime: 1 }, { 
    name: "checkins_venueId_checkInTime",
    background: true 
});

// ============================================================================
// USERS COLLECTION INDEXES
// ============================================================================


// 1. Email unique index (HIGHEST PRIORITY)
db.users.createIndex({ email: 1 }, { 
    name: "users_email_unique",
    unique: true,
    background: true 
});

// 2. Created At index (MEDIUM PRIORITY)
db.users.createIndex({ createdAt: 1 }, { 
    name: "users_createdAt",
    background: true 
});

// 3. Last Login index (MEDIUM PRIORITY)
db.users.createIndex({ lastLogin: 1 }, { 
    name: "users_lastLogin",
    background: true 
});

// 4. User preferences location geospatial index (LOW PRIORITY)
db.users.createIndex({ "profile.preferences.location": "2dsphere" }, { 
    name: "users_preferences_location",
    background: true,
    sparse: true 
});