// Initial strategic indexes for EventSphere

// 1) Geospatial index for event discovery
db.events.createIndex({ location: "2dsphere" }); // Enables $geoNear and $near queries

// 2) Text search across key fields
db.events.createIndex({ title: "text", description: "text", category: "text", tags: "text" }); // Relevance-ranked search

// 3) Date-based indexes for upcoming events and timelines
db.events.createIndex({ start_date: 1 }); // Range queries and sort
db.events.createIndex({ created_at: 1 }); // Timeline analytics

// 4) Compound indexes for common filters
db.events.createIndex({ category: 1, start_date: 1 }); // Category + date filter
db.events.createIndex({ organizer: 1, start_date: 1 }); // Organizer schedule
db.events.createIndex({ _id: 1, start_date: 1 }); // Cursor pagination

// 4.1) Polymorphic event type indexes
db.events.createIndex({ event_type: 1, start_date: 1 }); // Event type + date filter
db.events.createIndex({ event_type: 1, category: 1 }); // Event type + category filter

// 4.2) Extended Reference Pattern indexes
db.events.createIndex({ "venue_reference.venue_type": 1, start_date: 1 }); // Venue type + date filter
db.events.createIndex({ "venue_reference.city": 1, start_date: 1 }); // Venue city + date filter
db.events.createIndex({ "venue_reference.capacity": 1 }); // Venue capacity sorting

// 5) Reviews indexes for lookups and aggregations
db.reviews.createIndex({ event_id: 1 });
db.reviews.createIndex({ venue_id: 1 });
db.reviews.createIndex({ user_id: 1 });
db.reviews.createIndex({ rating: 1 });
db.reviews.createIndex({ created_at: 1 });
db.reviews.createIndex({ event_id: 1, rating: 1 }); // Event rating aggregations
db.reviews.createIndex({ venue_id: 1, rating: 1 }); // Venue rating aggregations

// 6) Check-ins indexes for analytics and duplicate prevention
db.checkins.createIndex({ event_id: 1 });
db.checkins.createIndex({ user_id: 1 });
db.checkins.createIndex({ venue_id: 1 });
db.checkins.createIndex({ check_in_time: 1 });
db.checkins.createIndex({ qr_code: 1 }, { unique: false });
db.checkins.createIndex({ event_id: 1, user_id: 1 }, { unique: true }); // Prevent duplicate check-ins per event/user
db.checkins.createIndex({ venue_id: 1, check_in_time: 1 }); // Venue time analytics
db.checkins.createIndex({ user_id: 1, check_in_time: 1 }); // User attendance patterns

// 7) Venues geospatial index
db.venues.createIndex({ location: "2dsphere" });

// 7.1) Polymorphic venue type indexes
db.venues.createIndex({ venue_type: 1, capacity: 1 }); // Venue type + capacity filter
db.venues.createIndex({ venue_type: 1, rating: 1 }); // Venue type + rating filter


