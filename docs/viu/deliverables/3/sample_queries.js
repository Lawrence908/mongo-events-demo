// Sample Queries Demonstrating Index Usage for EventSphere
// This file contains example queries that showcase the effectiveness of our indexing strategy

print("EventSphere Sample Queries - Demonstrating Index Usage");
print("========================================================");

// ============================================================================
// GEOSPATIAL QUERIES (Using 2dsphere indexes)
// ============================================================================

print("\n1. GEOSPATIAL QUERIES");
print("----------------------");

// Find events within 50km of New York City
print("Query: Find events within 50km of NYC");
const nycEvents = db.events.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-74.0060, 40.7128] },
      distanceField: "distance",
      maxDistance: 50000, // 50km in meters
      spherical: true,
      query: { status: "published" }
    }
  },
  { $limit: 10 }
]);
print("Index Used: {location: '2dsphere'}");
print("Result Count:", nycEvents.length);

// Find venues near a specific location
print("\nQuery: Find venues within 25km of San Francisco");
const sfVenues = db.venues.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-122.4194, 37.7749] },
      distanceField: "distance",
      maxDistance: 25000, // 25km in meters
      spherical: true,
      query: { venueType: "conferenceCenter" }
    }
  },
  { $limit: 5 }
]);
print("Index Used: {location: '2dsphere'}");
print("Result Count:", sfVenues.length);

// ============================================================================
// TEXT SEARCH QUERIES (Using text indexes)
// ============================================================================

print("\n2. TEXT SEARCH QUERIES");
print("-----------------------");

// Full-text search with relevance scoring
print("Query: Search for 'technology conference' events");
const techEvents = db.events.find(
  { 
    $text: { $search: "technology conference" },
    status: "published"
  },
  { 
    score: { $meta: "textScore" },
    title: 1,
    category: 1,
    startDate: 1
  }
).sort({ score: { $meta: "textScore" } }).limit(10);
print("Index Used: {title: 'text', description: 'text', category: 'text', tags: 'text'}");
print("Result Count:", techEvents.length);

// Search with specific category
print("\nQuery: Search for 'music' events with high relevance");
const musicEvents = db.events.find(
  { 
    $text: { $search: "music concert" },
    category: "Music"
  },
  { 
    score: { $meta: "textScore" },
    title: 1,
    startDate: 1
  }
).sort({ score: { $meta: "textScore" } }).limit(5);
print("Index Used: Text index + {category: 1, startDate: 1}");
print("Result Count:", musicEvents.length);

// ============================================================================
// COMPOUND QUERY PATTERNS (Using compound indexes)
// ============================================================================

print("\n3. COMPOUND QUERY PATTERNS");
print("---------------------------");

// Category + Date filtering
print("Query: Technology events this month");
const thisMonth = new Date();
const nextMonth = new Date();
nextMonth.setMonth(nextMonth.getMonth() + 1);

const techThisMonth = db.events.find({
  category: "Technology",
  startDate: { $gte: thisMonth, $lt: nextMonth },
  status: "published"
}).sort({ startDate: 1 }).limit(10);
print("Index Used: {category: 1, startDate: 1}");
print("Result Count:", techThisMonth.length);

// Event type + Date filtering (Polymorphic)
print("\nQuery: Virtual events next week");
const nextWeek = new Date();
nextWeek.setDate(nextWeek.getDate() + 7);

const virtualNextWeek = db.events.find({
  eventType: "virtual",
  startDate: { $gte: new Date(), $lt: nextWeek },
  status: "published"
}).sort({ startDate: 1 }).limit(10);
print("Index Used: {eventType: 1, startDate: 1}");
print("Result Count:", virtualNextWeek.length);

// Geospatial + Date filtering
print("\nQuery: Events near location this weekend");
const weekend = new Date();
weekend.setDate(weekend.getDate() + (6 - weekend.getDay())); // Next Saturday

const weekendEvents = db.events.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [-74.0060, 40.7128] },
      $maxDistance: 30000 // 30km
    }
  },
  startDate: { $gte: new Date(), $lt: weekend },
  status: "published"
}).limit(10);
print("Index Used: {location: '2dsphere', startDate: 1}");
print("Result Count:", weekendEvents.length);

// ============================================================================
// EXTENDED REFERENCE PATTERN QUERIES
// ============================================================================

print("\n4. EXTENDED REFERENCE PATTERN QUERIES");
print("--------------------------------------");

// Filter by venue type without joins
print("Query: Events at conference centers this month");
const conferenceEvents = db.events.find({
  "venueReference.venueType": "conferenceCenter",
  startDate: { $gte: thisMonth, $lt: nextMonth },
  status: "published"
}).sort({ startDate: 1 }).limit(10);
print("Index Used: {venueReference.venueType: 1, startDate: 1}");
print("Result Count:", conferenceEvents.length);

// Filter by venue city
print("\nQuery: Events in San Francisco");
const sfEvents = db.events.find({
  "venueReference.city": "San Francisco",
  status: "published"
}).sort({ startDate: 1 }).limit(10);
print("Index Used: {venueReference.city: 1, startDate: 1}");
print("Result Count:", sfEvents.length);

// ============================================================================
// PAGINATION QUERIES (Using cursor-based pagination)
// ============================================================================

print("\n5. PAGINATION QUERIES");
print("----------------------");

// Cursor-based pagination
print("Query: First page of events (cursor-based pagination)");
const firstPage = db.events.find({
  status: "published"
}).sort({ _id: 1, startDate: 1 }).limit(20);
print("Index Used: {_id: 1, startDate: 1}");
print("Result Count:", firstPage.length);

// Simulate next page using last document's _id
if (firstPage.length > 0) {
  const lastId = firstPage[firstPage.length - 1]._id;
  print("\nQuery: Next page using cursor");
  const nextPage = db.events.find({
    _id: { $gt: lastId },
    status: "published"
  }).sort({ _id: 1, startDate: 1 }).limit(20);
  print("Index Used: {_id: 1, startDate: 1}");
  print("Result Count:", nextPage.length);
}

// ============================================================================
// ANALYTICS QUERIES (Using aggregation-optimized indexes)
// ============================================================================

print("\n6. ANALYTICS QUERIES");
print("---------------------");

// Event rating aggregations
print("Query: Average rating for each event");
const eventRatings = db.reviews.aggregate([
  { $match: { eventId: { $exists: true } } },
  { $group: { 
    _id: "$eventId", 
    avgRating: { $avg: "$rating" },
    reviewCount: { $sum: 1 }
  }},
  { $match: { reviewCount: { $gte: 3 } } }, // Minimum 3 reviews
  { $sort: { avgRating: -1 } },
  { $limit: 10 }
]);
print("Index Used: {eventId: 1, rating: 1}");
print("Result Count:", eventRatings.length);

// Venue performance analytics
print("\nQuery: Venue attendance statistics");
const venueStats = db.checkins.aggregate([
  { $group: { 
    _id: "$venueId", 
    totalCheckins: { $sum: 1 },
    uniqueUsers: { $addToSet: "$userId" }
  }},
  { $project: { 
    venueId: "$_id", 
    totalCheckins: 1, 
    uniqueUsers: { $size: "$uniqueUsers" }
  }},
  { $sort: { totalCheckins: -1 } },
  { $limit: 10 }
]);
print("Index Used: {venueId: 1, checkInTime: 1}");
print("Result Count:", venueStats.length);

// User attendance patterns
print("\nQuery: Most active users (by check-in count)");
const activeUsers = db.checkins.aggregate([
  { $group: { 
    _id: "$userId", 
    checkinCount: { $sum: 1 },
    events: { $addToSet: "$eventId" }
  }},
  { $project: { 
    userId: "$_id", 
    checkinCount: 1, 
    uniqueEvents: { $size: "$events" }
  }},
  { $sort: { checkinCount: -1 } },
  { $limit: 10 }
]);
print("Index Used: {userId: 1, checkInTime: 1}");
print("Result Count:", activeUsers.length);

// ============================================================================
// CHECK-IN OPERATIONS (Using unique compound indexes)
// ============================================================================

print("\n7. CHECK-IN OPERATIONS");
print("-----------------------");

// Check-in validation (prevent duplicates)
print("Query: Check if user already checked into event");
const existingCheckin = db.checkins.findOne({
  eventId: ObjectId("68ddb640c00b1dff057fbefc"),
  userId: ObjectId("68ddb640c00b1dff057fb511")
});
print("Index Used: {eventId: 1, userId: 1} (unique)");
print("Duplicate Check Result:", existingCheckin ? "Already checked in" : "Can check in");

// QR code validation
print("\nQuery: Validate QR code for check-in");
const qrCheckin = db.checkins.findOne({
  qrCode: "QR-554361"
});
print("Index Used: {qrCode: 1}");
print("QR Code Validation:", qrCheckin ? "Valid QR code" : "Invalid QR code");

// ============================================================================
// POLYMORPHIC QUERIES (Using type-specific indexes)
// ============================================================================

print("\n8. POLYMORPHIC QUERIES");
print("-----------------------");

// Virtual events with platform filtering
print("Query: Zoom virtual events");
const zoomEvents = db.events.find({
  eventType: "virtual",
  "virtualDetails.platform": "Zoom",
  status: "published"
}).limit(10);
print("Index Used: {eventType: 1, startDate: 1}");
print("Result Count:", zoomEvents.length);

// Conference centers with specific amenities
print("\nQuery: Conference centers with video conferencing");
const confCenters = db.venues.find({
  venueType: "conferenceCenter",
  "conferenceCenterDetails.avEquipment": "Video Conferencing"
}).limit(10);
print("Index Used: {venueType: 1, capacity: 1}");
print("Result Count:", confCenters.length);

// ============================================================================
// SCHEMA VERSIONING QUERIES
// ============================================================================

print("\n9. SCHEMA VERSIONING QUERIES");
print("-----------------------------");

// Find documents by schema version
print("Query: Events using schema version 1.0");
const v1Events = db.events.find({
  schemaVersion: "1.0"
}).limit(5);
print("Index Used: {schemaVersion: 1}");
print("Result Count:", v1Events.length);

// Count documents by schema version
print("\nQuery: Count documents by schema version");
const schemaStats = db.events.aggregate([
  { $group: { _id: "$schemaVersion", count: { $sum: 1 } } },
  { $sort: { _id: 1 } }
]);
print("Index Used: {schemaVersion: 1}");
print("Schema Version Distribution:", schemaStats.length);

// ============================================================================
// PERFORMANCE ANALYSIS QUERIES
// ============================================================================

print("\n10. PERFORMANCE ANALYSIS");
print("-------------------------");

// Check index usage statistics
print("Query: Index usage statistics for events collection");
const indexStats = db.events.aggregate([{ $indexStats: {} }]);
print("Index Usage Statistics:");
indexStats.forEach(stat => {
  print(`  ${stat.name}: ${stat.accesses.ops} operations`);
});

// Check collection statistics
print("\nQuery: Collection statistics");
const collStats = db.events.stats();
print(`Events Collection:`);
print(`  Documents: ${collStats.count}`);
print(`  Size: ${(collStats.size / 1024 / 1024).toFixed(2)} MB`);
print(`  Indexes: ${collStats.nindexes}`);
print(`  Index Size: ${(collStats.totalIndexSize / 1024 / 1024).toFixed(2)} MB`);

print("\n========================================================");
print("Sample queries completed successfully!");
print("All queries demonstrate effective use of our indexing strategy.");
print("========================================================");
