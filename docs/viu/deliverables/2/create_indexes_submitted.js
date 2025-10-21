// Initial strategic indexes for EventSphere

// 1) Geospatial index for event discovery
db.events.createIndex({ location: "2dsphere" }); // Enables $geoNear and $near queries

// 2) Text search across key fields
db.events.createIndex({ title: "text", description: "text", category: "text", tags: "text" }); // Relevance-ranked search

// 3) Date-based indexes for upcoming events and timelines
db.events.createIndex({ startDate: 1 }); // Range queries and sort
db.events.createIndex({ createdAt: 1 }); // Timeline analytics

// 4) Compound indexes for common filters
db.events.createIndex({ category: 1, startDate: 1 }); // Category + date filter
db.events.createIndex({ organizer: 1, startDate: 1 }); // Organizer schedule
db.events.createIndex({ _id: 1, startDate: 1 }); // Cursor pagination

// 4.1) Polymorphic event type indexes
db.events.createIndex({ eventType: 1, startDate: 1 }); // Event type + date filter
db.events.createIndex({ eventType: 1, category: 1 }); // Event type + category filter

// 4.2) Extended Reference Pattern indexes
db.events.createIndex({ "venueReference.venueType": 1, startDate: 1 }); // Venue type + date filter
db.events.createIndex({ "venueReference.city": 1, startDate: 1 }); // Venue city + date filter
db.events.createIndex({ "venueReference.capacity": 1 }); // Venue capacity sorting

// 5) Reviews indexes for lookups and aggregations
db.reviews.createIndex({ eventId: 1 });
db.reviews.createIndex({ venueId: 1 });
db.reviews.createIndex({ userId: 1 });
db.reviews.createIndex({ rating: 1 });
db.reviews.createIndex({ createdAt: 1 });
db.reviews.createIndex({ eventId: 1, rating: 1 }); // Event rating aggregations
db.reviews.createIndex({ venueId: 1, rating: 1 }); // Venue rating aggregations

// 6) Check-ins indexes for analytics and duplicate prevention
db.checkins.createIndex({ eventId: 1 });
db.checkins.createIndex({ userId: 1 });
db.checkins.createIndex({ venueId: 1 });
db.checkins.createIndex({ checkInTime: 1 });
db.checkins.createIndex({ qrCode: 1 }, { unique: false });
db.checkins.createIndex({ eventId: 1, userId: 1 }, { unique: true }); // Prevent duplicate check-ins per event/user
db.checkins.createIndex({ venueId: 1, checkInTime: 1 }); // Venue time analytics
db.checkins.createIndex({ userId: 1, checkInTime: 1 }); // User attendance patterns

// 7) Venues geospatial index
db.venues.createIndex({ location: "2dsphere" });

// 7.1) Polymorphic venue type indexes
db.venues.createIndex({ venueType: 1, capacity: 1 }); // Venue type + capacity filter
db.venues.createIndex({ venueType: 1, rating: 1 }); // Venue type + rating filter


