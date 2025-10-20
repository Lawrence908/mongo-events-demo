# Design Patterns Used & Anti-Patterns Avoided in EventSphere

## Design Patterns Used

### 1. Extended Reference Pattern

**Implementation**: Events store denormalized venue data for performance optimization.

```javascript
// Event document with extended venue reference
{
  "_id": ObjectId("..."),
  "title": "Tech Conference 2024",
  "venueId": ObjectId("venue123"),
  "venueReference": {
    "name": "Convention Center",
    "city": "San Francisco",
    "capacity": 5000,
    "venueType": "conferenceCenter"
  },
  // ... other fields
}
```

**Benefits**:
- **Query Performance**: Avoid joins when filtering events by venue type or city
- **Reduced Lookups**: Venue information available in event queries without additional database calls
- **Filtering Capability**: Enable venue-based filtering without expensive joins
- **Consistency**: Reference data updated via application logic when venue changes

**Use Cases**:
- Filter events by venue type: "Show me all events at conference centers"
- Filter events by city: "Show me events in San Francisco"
- Sort events by venue capacity: "Show me events at large venues"

**Indexes Supporting This Pattern**:
- `{venueReference.venueType: 1, startDate: 1}`
- `{venueReference.city: 1, startDate: 1}`
- `{venueReference.capacity: 1}`

### 2. Computed Pattern

**Implementation**: Pre-calculated statistics stored in documents to improve query performance.

```javascript
// Event with computed statistics
{
  "_id": ObjectId("..."),
  "title": "Tech Conference 2024",
  "currentAttendees": 150,
  "maxAttendees": 200,
  "computedStats": {
    "totalTicketsSold": 180,
    "totalRevenue": 45000,
    "attendanceRate": 75.0,
    "reviewCount": 23,
    "averageRating": 4.2,
    "lastUpdated": ISODate("2024-01-15T10:30:00Z")
  }
}
```

**Benefits**:
- **Performance**: Eliminates expensive aggregations for dashboard queries
- **Consistency**: Single source of truth for statistics
- **Scalability**: Reduces database load during peak usage
- **Real-time Updates**: Statistics updated via application triggers

**Update Triggers**:
- Statistics recalculated when tickets are sold/refunded
- Statistics updated when reviews are added/updated
- Statistics refreshed when events are created/completed
- Statistics updated when check-ins occur

### 3. Polymorphic Pattern

**Implementation**: Single collection with type-specific fields for different entity types.

#### Event Polymorphism
```javascript
// Virtual event
{
  "eventType": "virtual",
  "virtualDetails": {
    "platform": "Zoom",
    "meetingUrl": "https://zoom.us/j/123456789",
    "recordingAvailable": true,
    "timezone": "PST"
  }
}

// Hybrid event
{
  "eventType": "hybrid",
  "hybridDetails": {
    "virtualCapacity": 500,
    "inPersonCapacity": 100,
    "virtualMeetingUrl": "https://teams.microsoft.com/j/987654321"
  }
}
```

#### Venue Polymorphism
```javascript
// Conference center venue
{
  "venueType": "conferenceCenter",
  "conferenceCenterDetails": {
    "breakoutRooms": 12,
    "avEquipment": ["Video Conferencing", "Projectors", "Whiteboards"],
    "cateringAvailable": true
  }
}

// Park venue
{
  "venueType": "park",
  "parkDetails": {
    "outdoorSpace": true,
    "parkingSpaces": 200,
    "restroomFacilities": true
  }
}
```

**Benefits**:
- **Schema Flexibility**: Different types can have specialized attributes
- **Query Efficiency**: Filter by type using discriminator field
- **Maintainability**: Single collection for related entity types
- **Extensibility**: Easy to add new types without schema changes

### 4. Schema Versioning Pattern

**Implementation**: All collections include `schemaVersion` field for future evolution.

```javascript
// All documents include schema version
{
  "_id": ObjectId("..."),
  "schemaVersion": "1.0",
  // ... other fields
}
```

**Benefits**:
- **Safe Evolution**: Add new fields without breaking existing data
- **Gradual Migration**: Update documents in batches by version
- **Rollback Capability**: Revert to previous schema if needed
- **Analytics**: Track adoption of new schema versions

**Migration Strategy**:
```javascript
// Find documents needing migration
db.events.find({ schemaVersion: { $ne: "1.0" } })

// Update documents to new schema version
db.events.updateMany(
  { schemaVersion: "0.9" },
  { $set: { schemaVersion: "1.0", newField: "defaultValue" } }
)
```

### 5. Bridge Collection Pattern

**Implementation**: `checkins` collection serves as bridge for many-to-many relationship between users and events.

```javascript
// Check-in document (bridge)
{
  "_id": ObjectId("..."),
  "eventId": ObjectId("event123"),
  "userId": ObjectId("user456"),
  "venueId": ObjectId("venue789"), // Denormalized for analytics
  "checkInTime": ISODate("2024-01-15T14:30:00Z"),
  "qrCode": "QR-123456",
  "ticketTier": "VIP",
  "checkInMethod": "qrCode",
  "metadata": {
    "deviceInfo": "iPhone",
    "ipAddress": "192.168.1.100",
    "staffVerified": true
  }
}
```

**Benefits**:
- **Analytics Flexibility**: Easy to query attendance patterns and user behavior
- **Query Performance**: Optimized indexes for common analytics queries
- **Scalability**: Avoids document size bloat in user or event collections
- **Data Integrity**: Centralized check-in logic with consistent validation

**Analytics Queries Enabled**:
- "Which users attended events at this venue last month?"
- "What's the average check-in time for this event type?"
- "How many repeat attendees do we have?"
- "Which events have the highest attendance rates?"

## Anti-Patterns Avoided

### 1. Over-Embedding Large Subdocuments

**Anti-Pattern**: Storing large, frequently changing data as embedded documents.

**What We Avoided**:
```javascript
// BAD: Embedding all user reviews in user document
{
  "_id": ObjectId("user123"),
  "email": "user@example.com",
  "reviews": [
    {
      "eventId": ObjectId("event1"),
      "rating": 5,
      "comment": "Great event!",
      "createdAt": ISODate("2024-01-01")
    },
    // ... potentially hundreds of reviews
  ]
}
```

**Why We Avoided It**:
- **Document Size Limit**: MongoDB has 16MB document size limit
- **Write Performance**: Updating user document becomes expensive
- **Memory Usage**: Large documents consume excessive RAM
- **Query Performance**: Filtering embedded arrays is inefficient

**Our Solution**: Separate `reviews` collection with references.

### 2. Over-Indexing (Too Many Indexes Slowing Down Writes)

**Anti-Pattern**: Creating indexes for every possible query without considering write performance.

**What We Avoided**:
```javascript
// BAD: Too many single-field indexes
db.events.createIndex({ "title": 1 })
db.events.createIndex({ "description": 1 })
db.events.createIndex({ "organizer": 1 })
db.events.createIndex({ "price": 1 })
db.events.createIndex({ "currency": 1 })
db.events.createIndex({ "isFree": 1 })
db.events.createIndex({ "status": 1 })
// ... many more single-field indexes
```

**Why We Avoided It**:
- **Write Performance**: Each index slows down insert/update operations
- **Storage Overhead**: Excessive index storage requirements
- **Memory Usage**: Too many indexes consume excessive RAM
- **Maintenance**: Complex index management and monitoring

**Our Solution**: Strategic compound indexes that support multiple query patterns.

### 3. Missing Indexes on Frequent Queries

**Anti-Pattern**: Not creating indexes for commonly executed queries.

**What We Avoided**:
```javascript
// BAD: Querying without proper indexes
db.events.find({
  "category": "Technology",
  "startDate": { $gte: new Date() },
  "location": {
    $near: {
      $geometry: { type: "Point", coordinates: [-74.0060, 40.7128] },
      $maxDistance: 50000
    }
  }
})
// Without proper compound indexes, this would be very slow
```

**Why We Avoided It**:
- **Query Performance**: Slow queries degrade user experience
- **Resource Usage**: Full collection scans consume excessive CPU and memory
- **Scalability**: Performance degrades as data grows

**Our Solution**: Comprehensive indexing strategy with compound indexes for common query patterns.

### 4. Using Regex Without Index Support

**Anti-Pattern**: Using regular expressions on unindexed fields.

**What We Avoided**:
```javascript
// BAD: Regex queries without proper indexing
db.events.find({ "title": /technology/i })
db.events.find({ "description": /conference/i })
```

**Why We Avoided It**:
- **Performance**: Regex queries without indexes are very slow
- **Scalability**: Performance degrades significantly with data growth
- **Resource Usage**: Full collection scans for pattern matching

**Our Solution**: Text indexes for full-text search with relevance scoring.

### 5. Inefficient Pagination

**Anti-Pattern**: Using offset-based pagination for large datasets.

**What We Avoided**:
```javascript
// BAD: Offset-based pagination
db.events.find().skip(10000).limit(20)
```

**Why We Avoided It**:
- **Performance**: Skip operations become slower as offset increases
- **Memory Usage**: MongoDB must process and discard skipped documents
- **Scalability**: Performance degrades significantly with large offsets

**Our Solution**: Cursor-based pagination with compound indexes.

```javascript
// GOOD: Cursor-based pagination
db.events.find({ "_id": { $gt: lastId } }).sort({ "_id": 1 }).limit(20)
```

### 6. Inconsistent Data Types

**Anti-Pattern**: Storing the same type of data in different formats.

**What We Avoided**:
```javascript
// BAD: Inconsistent date formats
{
  "startDate": "2024-01-15", // String
  "endDate": ISODate("2024-01-15T18:00:00Z"), // Date object
  "createdAt": 1705334400000 // Timestamp
}
```

**Why We Avoided It**:
- **Query Complexity**: Difficult to perform date range queries
- **Index Efficiency**: Inconsistent types reduce index effectiveness
- **Data Integrity**: Type mismatches can cause application errors

**Our Solution**: Consistent use of `Date` objects throughout the schema.

### 7. Denormalization Without Strategy

**Anti-Pattern**: Randomly denormalizing data without considering access patterns.

**What We Avoided**:
```javascript
// BAD: Unnecessary denormalization
{
  "eventId": ObjectId("event123"),
  "userId": ObjectId("user456"),
  "userEmail": "user@example.com", // Unnecessary denormalization
  "userFirstName": "John", // Unnecessary denormalization
  "userLastName": "Doe", // Unnecessary denormalization
  "eventTitle": "Tech Conference", // Unnecessary denormalization
  "eventDescription": "A great tech event" // Unnecessary denormalization
}
```

**Why We Avoided It**:
- **Data Consistency**: Multiple sources of truth for the same data
- **Storage Overhead**: Unnecessary data duplication
- **Maintenance**: Complex update logic to keep denormalized data in sync

**Our Solution**: Strategic denormalization only where it provides significant performance benefits (e.g., `venueReference` in events).

## Best Practices Demonstrated

1. **Query-Driven Design**: Indexes designed for actual query patterns
2. **Compound Indexes**: Optimize multi-field queries efficiently
3. **Cursor Pagination**: Better than offset-based for large datasets
4. **Geospatial Optimization**: 2dsphere indexes for location queries
5. **Text Search**: Multi-field indexes with relevance scoring
6. **Polymorphic Design**: Flexible schema for different entity types
7. **Schema Versioning**: Future-proof design for evolution
8. **Strategic Denormalization**: Only where performance benefits are significant
9. **Data Integrity**: Proper constraints and validation
10. **Performance Monitoring**: Index usage tracking and optimization
