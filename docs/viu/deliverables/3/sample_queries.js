// Sample Queries for EventSphere
// These queries demonstrate the usage of the indexes created in the create_indexes.js file.

// ============================================================================
// GEOSPATIAL QUERIES
// ============================================================================

// Find events near NYC using 2dsphere index
db.events.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [-74.0060, 40.7128] },
      $maxDistance: 50000
    }
  },
  status: "published"
}).limit(10);

// Find conference centers near San Francisco
db.venues.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [-122.4194, 37.7749] },
      $maxDistance: 25000
    }
  },
  venueType: "conferenceCenter"
}).limit(5);

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
// REVIEW QUERIES
// ============================================================================

// Find reviews for a specific event
db.reviews.find({
  eventId: ObjectId("68ddb640c00b1dff057fbefc")
}).sort({ rating: -1 }).limit(10);

// Find reviews by a specific user
db.reviews.find({
  userId: ObjectId("68ddb640c00b1dff057fb511")
}).sort({ createdAt: -1 });

// Find high-rated reviews for events
db.reviews.find({
  eventId: { $exists: true },
  rating: { $gte: 4 }
}).sort({ rating: -1, createdAt: -1 }).limit(10);

// ============================================================================
// CHECK-IN OPERATIONS
// ============================================================================

// Check if user already checked into event
db.checkins.findOne({
  eventId: ObjectId("68ddb640c00b1dff057fbefc"),
  userId: ObjectId("68ddb640c00b1dff057fb511")
});

// Find all check-ins for a specific event
db.checkins.find({
  eventId: ObjectId("68ddb640c00b1dff057fbefc")
}).sort({ checkInTime: -1 });

// Find all check-ins by a specific user
db.checkins.find({
  userId: ObjectId("68ddb640c00b1dff057fb511")
}).sort({ checkInTime: -1 });

// ============================================================================
// VENUE QUERIES
// ============================================================================

// Find venues by type and capacity
db.venues.find({
  venueType: "conferenceCenter",
  capacity: { $gte: 500 }
}).sort({ capacity: -1 });

// Find venues by type and rating
db.venues.find({
  venueType: "hotel",
  rating: { $gte: 4 }
}).sort({ rating: -1 });

// Text search for venues
db.venues.find({
  $text: { $search: "conference center downtown" }
}).sort({ score: { $meta: "textScore" } }).limit(5);

// ============================================================================
// USER QUERIES
// ============================================================================

// Find users by email (unique index)
db.users.findOne({ email: "user@example.com" });

// Find recently created users
db.users.find({
  createdAt: { $gte: new Date(Date.now() - 30*24*60*60*1000) }
}).sort({ createdAt: -1 });

// Find users with recent login activity
db.users.find({
  lastLogin: { $gte: new Date(Date.now() - 7*24*60*60*1000) }
}).sort({ lastLogin: -1 });
