# MongoDB Database Design - Events Demo

## Overview
This document outlines the comprehensive database design for the MongoDB Events Demo, showcasing advanced MongoDB features including geospatial queries, text search, real-time updates, and performance optimization. The design demonstrates real-world applicability for event management systems while highlighting key NoSQL advantages over traditional relational databases.

## Why NoSQL (MongoDB) for Event Management

### Schema Flexibility
- **Dynamic Event Attributes**: Each event can have unique metadata, pricing tiers, and custom fields without schema migrations
- **Embedded Documents**: Tickets, attendee lists, and check-ins stored as subdocuments for optimal read performance
- **Future-Proof Design**: Easy to add new event types (virtual, hybrid, recurring) without breaking existing data

### Geospatial Superiority
- **Native GeoJSON Support**: Superior handling of location data compared to relational databases
- **Complex Geospatial Queries**: Radius-based discovery, venue proximity, and geographic analytics
- **Map Integration**: Direct compatibility with mapping libraries and GeoJSON standards

### Performance Benefits
- **Reduced Joins**: Embedded documents eliminate complex table joins
- **Horizontal Scaling**: Sharding by geography or event date for massive scale
- **Flexible Indexing**: Compound indexes optimized for real-world query patterns

## Database Collections & Schema Design

### Primary Collection: `events`
```javascript
{
  "_id": ObjectId,           // Globally unique, timestamped identifier
  "title": String,           // Event title (indexed for text search) - REQUIRED
  "description": String,     // Event description (indexed for text search) - OPTIONAL
  "category": String,        // Event category (indexed) - REQUIRED
  "location": {              // GeoJSON Point for geospatial queries - REQUIRED
    "type": "Point",         // Must be "Point"
    "coordinates": [longitude, latitude]  // [lng, lat] with bounds validation
  },
  "venue_id": ObjectId,      // Reference to venues collection - OPTIONAL
  "start_date": Date,        // Event start time (indexed) - REQUIRED
  "end_date": Date,          // Event end time - OPTIONAL
  "organizer": String,       // Event organizer (indexed) - OPTIONAL
  "max_attendees": Number,   // Maximum attendees (indexed) - OPTIONAL
  "tickets": [{              // Embedded subdocuments for performance - OPTIONAL
    "tier": String,          // "General", "VIP", "Early Bird" - REQUIRED
    "price": Number,         // Price >= 0 - REQUIRED
    "available": Number,     // Available tickets >= 0 - REQUIRED
    "sold": Number           // Sold tickets >= 0 - REQUIRED
  }],
  "attendees": [{            // Embedded for quick display - OPTIONAL
    "user_id": ObjectId,     // Reference to user - REQUIRED
    "checked_in": Boolean,   // Check-in status - REQUIRED
    "check_in_time": Date    // Check-in timestamp - OPTIONAL
  }],
  "tags": [String],          // Event tags (indexed for text search) - OPTIONAL
  "metadata": {              // Flexible schema for custom attributes - OPTIONAL
    "virtual": Boolean,
    "recurring": Boolean,
    "age_restriction": String,
    "dress_code": String
  },
  "created_at": Date,        // Document creation time (indexed) - REQUIRED
  "updated_at": Date         // Last update time - REQUIRED
}
```

### Supporting Collections

#### `venues` Collection
```javascript
{
  "_id": ObjectId,
  "name": String,            // Venue name - REQUIRED
  "address": {               // Complete address - REQUIRED
    "street": String,        // Street address - REQUIRED
    "city": String,          // City - REQUIRED
    "state": String,         // State/Province - REQUIRED
    "zip": String,           // ZIP/Postal code - REQUIRED
    "country": String        // Country - REQUIRED
  },
  "location": {              // GeoJSON Point - REQUIRED
    "type": "Point",         // Must be "Point"
    "coordinates": [longitude, latitude]  // [lng, lat] with bounds validation
  },
  "capacity": Number,        // Venue capacity - OPTIONAL
  "amenities": [String],     // "WiFi", "Parking", "Accessible" - OPTIONAL
  "contact": {               // Contact information - OPTIONAL
    "phone": String,
    "email": String,
    "website": String
  },
  "created_at": Date         // Document creation time - REQUIRED
}
```

#### `checkins` Collection
```javascript
{
  "_id": ObjectId,
  "event_id": ObjectId,      // Reference to events - REQUIRED
  "user_id": ObjectId,       // Reference to users - REQUIRED
  "check_in_time": Date,     // Check-in timestamp - REQUIRED
  "qr_code": String,         // Unique QR code for check-in - REQUIRED
  "ticket_tier": String,     // Ticket tier used - OPTIONAL
  "location": {              // Check-in location (if different from event) - OPTIONAL
    "type": "Point",         // Must be "Point"
    "coordinates": [longitude, latitude]  // [lng, lat] with bounds validation
  }
}
```

#### `users` Collection
```javascript
{
  "_id": ObjectId,
  "email": String,           // Unique identifier - REQUIRED
  "profile": {               // User profile - REQUIRED
    "first_name": String,    // First name - REQUIRED
    "last_name": String,     // Last name - REQUIRED
    "preferences": {         // User preferences - OPTIONAL
      "categories": [String], // Preferred event categories - OPTIONAL
      "location": {          // User location for discovery - OPTIONAL
        "type": "Point",     // Must be "Point"
        "coordinates": [longitude, latitude]  // [lng, lat] with bounds validation
      },
      "radius_km": Number    // Search radius in kilometers - OPTIONAL
    }
  },
  "created_at": Date,        // Account creation time - REQUIRED
  "last_login": Date         // Last login timestamp - OPTIONAL
}
```

## Schema Validation & Relationships

### Document Relationships Strategy

#### Embedding vs Referencing
- **Embedded Documents** (for frequently accessed, tightly bound data):
  - `tickets[]` in events - always displayed together
  - `attendees[]` in events - quick RSVP display
  - `address` in venues - always needed with venue info

- **Referenced Documents** (for large or shared data):
  - `venue_id` in events - venues shared across multiple events
  - `user_id` in checkins - users referenced across many events
  - `event_id` in checkins - events referenced by many check-ins

### Schema Validation Rules

All collections enforce comprehensive JSON Schema validation with the following key features:

#### Coordinate Bounds Validation
- **Longitude**: Must be between -180 and 180 degrees
- **Latitude**: Must be between -90 and 90 degrees
- **GeoJSON Structure**: All location fields must be valid GeoJSON Point objects
- **Coordinate Arrays**: Must contain exactly 2 elements [longitude, latitude]

#### Required Fields Enforcement
- **Events**: `title`, `category`, `location`, `start_date`, `created_at`, `updated_at`
- **Venues**: `name`, `location`, `address`, `created_at`
- **Users**: `email`, `profile`, `created_at`
- **Checkins**: `event_id`, `user_id`, `check_in_time`, `qr_code`

#### Data Type and Range Validation
- **String Lengths**: Enforced min/max lengths for all text fields
- **Numeric Ranges**: Positive values for counts, prices, and capacities
- **Email Format**: Valid email pattern for user accounts
- **Date Logic**: End dates must be after start dates
- **Array Constraints**: Proper array structures for coordinates and tags

#### Example: Events Collection Validation
```javascript
{
  $jsonSchema: {
    bsonType: "object",
    required: ["title", "category", "location", "start_date", "created_at", "updated_at"],
    properties: {
      title: {
        bsonType: "string",
        minLength: 1,
        maxLength: 200
      },
      location: {
        bsonType: "object",
        required: ["type", "coordinates"],
        properties: {
          type: { enum: ["Point"] },
          coordinates: {
            bsonType: "array",
            items: { bsonType: "double" },
            minItems: 2,
            maxItems: 2
          }
        }
      },
      start_date: { bsonType: "date" },
      max_attendees: { bsonType: "int", minimum: 1 }
    }
  }
}
```

**Implementation**: Schema validation is automatically applied to all collections via `app/schema_validation.py` and enforced at the database level through MongoDB's native JSON Schema validation.

### ObjectId Usage Strategy
- **Globally Unique**: No auto-increment IDs that don't scale across shards
- **Timestamped**: ObjectId contains creation timestamp for sorting
- **Efficient**: 12-byte identifier with built-in uniqueness
- **Distributed**: No coordination needed for ID generation

## Index Strategy

### 1. Geospatial Index
```javascript
db.events.createIndex({"location": "2dsphere"})
```
**Purpose**: Enables geospatial queries using `$geoNear` aggregation
**Queries**: Find events within radius, location-based filtering

### 2. Text Search Index
```javascript
db.events.createIndex({
  "title": "text",
  "description": "text", 
  "category": "text",
  "tags": "text"
})
```
**Purpose**: Full-text search across multiple fields
**Queries**: Search events by keywords, relevance scoring

### 3. Date-based Indexes
```javascript
db.events.createIndex({"start_date": 1})
db.events.createIndex({"created_at": 1})
```
**Purpose**: Efficient date range queries and sorting
**Queries**: Upcoming events, date filtering, chronological sorting

### 4. Compound Indexes for Common Query Patterns
```javascript
// Category + Date filtering
db.events.createIndex({"category": 1, "start_date": 1})

// Geospatial + Date filtering  
db.events.createIndex({"location": "2dsphere", "start_date": 1})

// Organizer + Date filtering
db.events.createIndex({"organizer": 1, "start_date": 1})

// Analytics queries
db.events.createIndex({"category": 1, "created_at": 1})
db.events.createIndex({"start_date": 1, "category": 1})
```
**Purpose**: Optimize compound queries without index intersection
**Queries**: "Tech events this weekend", "Events near me next month"

### 5. Cursor-based Pagination Support
```javascript
db.events.createIndex({"_id": 1, "start_date": 1})
```
**Purpose**: Efficient cursor-based pagination
**Queries**: Large result set pagination without performance degradation

### 6. Array and Filtering Indexes
```javascript
db.events.createIndex({"tags": 1})        // Tag filtering
db.events.createIndex({"max_attendees": 1}) // Capacity filtering
db.events.createIndex({"end_date": 1})     // End date queries
```
**Purpose**: Support filtering and aggregation queries
**Queries**: Events by tags, capacity-based filtering

## Query Patterns & Performance

### 1. Geospatial Queries
```javascript
// Find events within 50km of NYC
db.events.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-74.0060, 40.7128] },
      distanceField: "distance",
      maxDistance: 50000,
      spherical: true
    }
  }
])
```
**Index Used**: `{"location": "2dsphere"}`
**Performance**: O(log n) - Excellent for large datasets

### 2. Text Search with Relevance
```javascript
db.events.find(
  { $text: { $search: "technology conference" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } })
```
**Index Used**: Text index on title, description, category, tags
**Performance**: O(log n) with relevance scoring

### 3. Compound Queries
```javascript
// Tech events this weekend near location
db.events.find({
  "category": "Technology",
  "start_date": { $gte: friday, $lte: sunday },
  "location": {
    $near: {
      $geometry: { type: "Point", coordinates: [lng, lat] },
      $maxDistance: 50000
    }
  }
})
```
**Index Used**: `{"location": "2dsphere", "start_date": 1}`
**Performance**: Single index scan, very efficient

### 4. Cursor-based Pagination
```javascript
// First page
db.events.find().sort({"_id": 1}).limit(50)

// Next page using cursor
db.events.find({"_id": {$gt: lastId}}).sort({"_id": 1}).limit(50)
```
**Index Used**: `{"_id": 1, "start_date": 1}`
**Performance**: O(log n) regardless of page number

### 5. Analytics Aggregations
```javascript
// Peak event times
db.events.aggregate([
  {
    $group: {
      _id: {
        hour: { $hour: "$start_date" },
        dayOfWeek: { $dayOfWeek: "$start_date" }
      },
      count: { $sum: 1 }
    }
  },
  { $sort: { count: -1 } }
])
```
**Index Used**: `{"start_date": 1}`
**Performance**: Efficient with proper date indexing

## Real-time Features

### MongoDB Change Streams
```javascript
// Watch for changes
db.events.watch([
  { $match: { "operationType": { $in: ["insert", "update", "delete"] } } }
])
```
**Purpose**: Real-time event notifications via WebSockets
**Features**: Live updates, location-based subscriptions, category filtering

### WebSocket Integration
- **Events Namespace**: Real-time event updates
- **Analytics Namespace**: Live analytics updates
- **Location Rooms**: Subscribe to events in specific areas
- **Category Rooms**: Subscribe to specific event categories

## Performance Characteristics

### Expected Performance (10,000+ events)
- **Geospatial queries**: < 50ms
- **Text search**: < 100ms  
- **Compound queries**: < 75ms
- **Pagination**: < 25ms (cursor-based)
- **Analytics**: < 200ms
- **Real-time updates**: < 10ms latency

### Scalability Considerations
- **Index size**: ~20% of collection size
- **Memory usage**: Indexes cached in RAM
- **Write performance**: Minimal impact with proper indexing
- **Sharding**: Ready for horizontal scaling

## CAP Theorem & Consistency Trade-offs

### Event Management System Priorities
- **Availability**: Users must be able to browse and search events even during partial outages
- **Partition Tolerance**: System must handle network partitions gracefully
- **Consistency**: Eventual consistency acceptable for most operations

### Consistency Levels by Operation
- **Critical (Strong Consistency)**: Ticket booking, seat availability, payment processing
- **Important (Eventual Consistency)**: Check-in status, attendee counts, real-time analytics
- **Acceptable (Eventually Consistent)**: Event recommendations, search results, social features

### Transaction Strategy
```javascript
// Multi-document transaction for ticket booking
session = client.startSession();
session.startTransaction();
try {
  // 1. Check seat availability
  // 2. Deduct available seats
  // 3. Create check-in record
  // 4. Update attendee list
  session.commitTransaction();
} catch (error) {
  session.abortTransaction();
}
```

## Industry Alignment & Real-World Applicability

### Similar Production Systems
- **Eventbrite**: Uses MongoDB for event discovery and geospatial queries
- **Meetup**: Leverages document stores for flexible event schemas
- **Airbnb Experiences**: GeoJSON and compound indexes for location-based discovery

### Production-Ready Features
- **Horizontal Scaling**: Sharding by geography (`location`) or time (`start_date`)
- **Caching Strategy**: Redis for popular events and search results
- **CDN Integration**: Static assets and event images
- **Monitoring**: Query performance and index usage analytics

### Future Enhancement Readiness
- **Authentication**: JWT tokens with user preferences
- **Payment Processing**: Integration with Stripe/PayPal (separate SQL database)
- **Notifications**: Real-time push notifications via WebSockets
- **Social Features**: User connections, event sharing, reviews
- **Analytics**: Advanced reporting and business intelligence

## Best Practices Demonstrated

1. **Query-driven design**: Indexes designed for actual query patterns
2. **Compound indexes**: Optimize multi-field queries
3. **Cursor pagination**: Better than offset-based for large datasets
4. **Geospatial optimization**: 2dsphere indexes for location queries
5. **Text search**: Multi-field indexes with relevance scoring
6. **Real-time updates**: Change streams for live data
7. **Analytics optimization**: Aggregation-friendly indexes
8. **Schema flexibility**: Embedded vs referenced documents based on access patterns
9. **Transaction boundaries**: Critical operations use ACID transactions
10. **Scalability planning**: Sharding strategy for horizontal growth

## Testing & Validation

Run performance tests:
```bash
python test_performance.py
```

Generate test data:
```bash
python generate_test_data.py
```

## Polyglot Persistence Strategy

### Database Specialization
- **MongoDB**: Event metadata, geospatial queries, flexible schemas, real-time updates
- **PostgreSQL/MySQL**: User authentication, payment processing, financial transactions
- **Redis**: Session management, caching, real-time counters
- **Elasticsearch**: Advanced search, analytics, recommendation engine

### Data Flow Architecture
```
User Request → API Gateway → MongoDB (Events) → Redis (Cache)
                    ↓
            PostgreSQL (Users/Payments) → Elasticsearch (Search)
```

## Future Enhancement Roadmap

### Phase 1: Core Features (Current)
- ✅ Event CRUD operations
- ✅ Geospatial discovery
- ✅ Text search and filtering
- ✅ Real-time updates
- ✅ Analytics and reporting

### Phase 2: User Management
- 🔄 User authentication and profiles
- 🔄 Event creation and management
- 🔄 RSVP and ticket booking
- 🔄 Check-in system with QR codes

### Phase 3: Advanced Features
- 📋 Recommendation engine
- 📋 Social features and sharing
- 📋 Payment processing integration
- 📋 Mobile app with offline support

### Phase 4: Enterprise Features
- 📋 Multi-tenant architecture
- 📋 Advanced analytics dashboard
- 📋 API rate limiting and monitoring
- 📋 Automated scaling and load balancing

This design showcases comprehensive MongoDB capabilities while maintaining excellent performance characteristics for a real-world event management application. The architecture demonstrates deep understanding of NoSQL principles, industry best practices, and production-ready scalability considerations.
