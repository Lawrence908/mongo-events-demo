// Sample Queries for EventSphere - Demonstrating Index Usage
// Deliverable 3 - Indexing, Workload Analysis & Relationship Design

// ============================================================================
// GEOSPATIAL QUERIES
// ============================================================================

// Find events near NYC using 2dsphere index
db.events.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-74.0060, 40.7128] },
      distanceField: "distance",
      maxDistance: 50000,
      spherical: true,
      query: { status: "published" }
    }
  },
  { $limit: 10 }
]);

// Find conference centers near San Francisco
db.venues.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-122.4194, 37.7749] },
      distanceField: "distance",
      maxDistance: 25000,
      spherical: true,
      query: { venueType: "conferenceCenter" }
    }
  },
  { $limit: 5 }
]);

// ============================================================================
// TEXT SEARCH QUERIES
// ============================================================================

// Full-text search for technology events
db.events.find(
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

// ============================================================================
// COMPOUND QUERY PATTERNS
// ============================================================================

// Technology events this month
db.events.find({
  category: "Technology",
  startDate: { $gte: new Date(), $lt: new Date(Date.now() + 30*24*60*60*1000) },
  status: "published"
}).sort({ startDate: 1 }).limit(10);

// Virtual events next week
db.events.find({
  eventType: "virtual",
  startDate: { $gte: new Date(), $lt: new Date(Date.now() + 7*24*60*60*1000) },
  status: "published"
}).sort({ startDate: 1 }).limit(10);

// ============================================================================
// EXTENDED REFERENCE PATTERN QUERIES
// ============================================================================

// Events at conference centers
db.events.find({
  "venueReference.venueType": "conferenceCenter",
  startDate: { $gte: new Date() },
  status: "published"
}).sort({ startDate: 1 }).limit(10);

// ============================================================================
// PAGINATION QUERIES
// ============================================================================

// First page of events
db.events.find({
  status: "published"
}).sort({ _id: 1, startDate: 1 }).limit(20);

// ============================================================================
// ANALYTICS QUERIES
// ============================================================================

// Average rating per event
db.reviews.aggregate([
  { $match: { eventId: { $exists: true } } },
  { $group: { 
    _id: "$eventId", 
    avgRating: { $avg: "$rating" },
    reviewCount: { $sum: 1 }
  }},
  { $match: { reviewCount: { $gte: 3 } } },
  { $sort: { avgRating: -1 } },
  { $limit: 10 }
]);

// ============================================================================
// CHECK-IN OPERATIONS
// ============================================================================

// Check if user already checked into event
db.checkins.findOne({
  eventId: ObjectId("68ddb640c00b1dff057fbefc"),
  userId: ObjectId("68ddb640c00b1dff057fb511")
});
