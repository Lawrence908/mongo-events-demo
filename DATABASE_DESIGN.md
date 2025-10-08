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
  "eventType": String,      // Polymorphic discriminator - REQUIRED
                              // Values: "inPerson", "virtual", "hybrid", "recurring"
  "schemaVersion": String,   // Schema versioning - REQUIRED (currently "1.0")
  "location": {              // GeoJSON Point for geospatial queries - REQUIRED
    "type": "Point",         // Must be "Point"
    "coordinates": [longitude, latitude]  // [lng, lat] with bounds validation
  },
  "venueId": ObjectId,       // Reference to venues collection - OPTIONAL
  "venueReference": {       // Extended reference data for performance - OPTIONAL
    "name": String,          // Venue name for quick display
    "city": String,          // Venue city for filtering
    "capacity": Number,      // Venue capacity for sorting
    "venueType": String     // Venue type for polymorphic queries
  },
  "startDate": Date,        // Event start time (indexed) - REQUIRED
  "endDate": Date,          // Event end time - OPTIONAL
  "organizer": String,       // Event organizer (indexed) - OPTIONAL
  "maxAttendees": Number,   // Maximum attendees (indexed) - OPTIONAL
  "currentAttendees": Number, // Current number of attendees - OPTIONAL
  "price": Number,           // Event price - OPTIONAL
  "currency": String,        // Currency code (e.g., "USD") - OPTIONAL
  "isFree": Boolean,        // Whether event is free - OPTIONAL
  "status": String,          // Event status ("draft", "published", "cancelled", "completed") - OPTIONAL
  
  // Computed fields for performance
  "computedStats": {        // Pre-calculated statistics - OPTIONAL
    "totalTicketsSold": Number,    // Sum of all sold tickets
    "totalRevenue": Number,         // Calculated from ticket sales
    "attendanceRate": Number,       // currentAttendees / maxAttendees
    "reviewCount": Number,          // Number of reviews
    "averageRating": Number,        // Average review rating
    "lastUpdated": Date             // When stats were last calculated
  },
  "tickets": [{              // Embedded subdocuments for performance - OPTIONAL
    "tier": String,          // "General", "VIP", "Early Bird" - REQUIRED
    "price": Number,         // Price >= 0 - REQUIRED
    "available": Number,     // Available tickets >= 0 - REQUIRED
    "sold": Number           // Sold tickets >= 0 - REQUIRED
  }],
  "attendees": [{            // Embedded for quick display - OPTIONAL
    "userId": ObjectId,     // Reference to user - REQUIRED
    "checkedIn": Boolean,   // Check-in status - REQUIRED
    "checkInTime": Date    // Check-in timestamp - OPTIONAL
  }],
  "tags": [String],          // Event tags (indexed for text search) - OPTIONAL
  
  // Polymorphic type-specific fields
  "virtualDetails": {       // For virtual events - OPTIONAL
    "platform": String,      // "Zoom", "Teams", "WebEx", etc.
    "meetingUrl": String,   // Virtual meeting URL
    "recordingAvailable": Boolean,
    "timezone": String       // Event timezone
  },
  "recurringDetails": {     // For recurring events - OPTIONAL
    "frequency": String,     // "daily", "weekly", "monthly", "yearly"
    "endRecurrence": Date,  // When recurrence ends
    "exceptions": [Date]     // Dates to skip
  },
  "hybridDetails": {        // For hybrid events - OPTIONAL
    "virtualCapacity": Number,     // Max virtual attendees
    "inPersonCapacity": Number,   // Max in-person attendees
    "virtualMeetingUrl": String   // Virtual meeting URL
  },
  "metadata": {              // General metadata - OPTIONAL
    "ageRestriction": String,
    "dressCode": String,
    "accessibilityFeatures": [String]
  },
  "createdAt": Date,        // Document creation time (indexed) - REQUIRED
  "updatedAt": Date         // Last update time - REQUIRED
}
```

### Supporting Collections

#### `venues` Collection
```javascript
{
  "_id": ObjectId,
  "name": String,            // Venue name - REQUIRED
  "venueType": String,      // Polymorphic discriminator - REQUIRED
                              // Values: "conferenceCenter", "park", "restaurant", 
                              //         "virtualSpace", "stadium", "theater"
  "schemaVersion": String,   // Schema versioning - REQUIRED (currently "1.0")
  "description": String,     // Venue description - OPTIONAL
  "address": {               // Complete address - REQUIRED
    "street": String,        // Street address - REQUIRED
    "city": String,          // City - REQUIRED
    "state": String,         // State/Province - REQUIRED
    "zipCode": String,      // ZIP/Postal code - REQUIRED
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
  "pricing": {               // Venue pricing information - OPTIONAL
    "hourlyRate": Number,
    "dailyRate": Number,
    "currency": String
  },
  "availability": {          // Venue availability schedule - OPTIONAL
    "monday": {"open": String, "close": String},
    "tuesday": {"open": String, "close": String},
    // ... other days
  },
  "rating": Number,          // Venue rating (1-5) - OPTIONAL
  "reviewCount": Number,    // Number of reviews - OPTIONAL
  
  // Computed fields for performance
  "computedStats": {        // Pre-calculated statistics - OPTIONAL
    "totalEventsHosted": Number,    // Number of events at this venue
    "averageAttendance": Number,     // Average attendance per event
    "revenueGenerated": Number,      // Total revenue from events
    "lastEventDate": Date,          // Most recent event date
    "lastUpdated": Date              // When stats were last calculated
  },
  
  // Polymorphic type-specific fields
  "conferenceCenterDetails": {  // For conference centers - OPTIONAL
    "meetingRooms": Number,      // Number of meeting rooms
    "exhibitionSpace": Number,   // Exhibition space in sq ft
    "cateringAvailable": Boolean,
    "avEquipment": [String]      // Available AV equipment
  },
  "parkDetails": {              // For parks - OPTIONAL
    "parkType": String,         // "national", "state", "city", "recreation"
    "activities": [String],      // Available activities
    "permitRequired": Boolean,  // Whether permits are needed
    "seasonalHours": Boolean    // Whether hours change seasonally
  },
  "virtualSpaceDetails": {     // For virtual spaces - OPTIONAL
    "platform": String,          // "Zoom", "Teams", "WebEx", etc.
    "maxParticipants": Number,  // Max virtual participants
    "recordingCapability": Boolean,
    "breakoutRooms": Number     // Number of breakout rooms
  },
  "createdAt": Date,        // Document creation time - REQUIRED
  "updatedAt": Date         // Last update time - REQUIRED
}
```

#### `checkins` Collection
```javascript
{
  "_id": ObjectId,
  "eventId": ObjectId,      // Reference to events - REQUIRED
  "userId": ObjectId,       // Reference to users - REQUIRED
  "venueId": ObjectId,      // Reference to venues (denormalized for analytics) - REQUIRED
  "checkInTime": Date,     // Check-in timestamp - REQUIRED
  "qrCode": String,         // Unique QR code for check-in - REQUIRED
  "ticketTier": String,     // Ticket tier used - OPTIONAL
  "checkInMethod": String, // "qr_code", "manual", "mobile_app" - OPTIONAL
  "location": {              // Check-in location (if different from event) - OPTIONAL
    "type": "Point",         // Must be "Point"
    "coordinates": [longitude, latitude]  // [lng, lat] with bounds validation
  },
  "metadata": {              // Additional check-in context - OPTIONAL
    "deviceInfo": String,   // Mobile device or browser info
    "ipAddress": String,    // For security/analytics
    "staffVerified": Boolean // Manual verification by staff
  },
  "schemaVersion": String,   // Schema versioning - REQUIRED (currently "1.0")
  "createdAt": Date         // Record creation time - REQUIRED
}
```

#### `users` Collection
```javascript
{
  "_id": ObjectId,
  "email": String,           // Unique identifier - REQUIRED
  "schemaVersion": String,   // Schema versioning - REQUIRED (currently "1.0")
  "profile": {               // User profile - REQUIRED
    "firstName": String,    // First name - REQUIRED
    "lastName": String,     // Last name - REQUIRED
    "preferences": {         // User preferences - OPTIONAL
      "categories": [String], // Preferred event categories - OPTIONAL
      "location": {          // User location for discovery - OPTIONAL
        "type": "Point",     // Must be "Point"
        "coordinates": [longitude, latitude]  // [lng, lat] with bounds validation
      },
      "radiusKm": Number    // Search radius in kilometers - OPTIONAL
    }
  },
  "createdAt": Date,        // Account creation time - REQUIRED
  "lastLogin": Date         // Last login timestamp - OPTIONAL
}
```

#### `reviews` Collection
```javascript
{
  "_id": ObjectId,
  "eventId": ObjectId,      // Reference to events - REQUIRED (if reviewing event)
  "venueId": ObjectId,      // Reference to venues - REQUIRED (if reviewing venue)
  "userId": ObjectId,       // Reference to users - REQUIRED
  "rating": Number,          // Rating 1-5 - REQUIRED
  "comment": String,         // Review text - OPTIONAL
  "schemaVersion": String,   // Schema versioning - REQUIRED (currently "1.0")
  "createdAt": Date,        // Review creation time - REQUIRED
  "updatedAt": Date         // Last update time - REQUIRED
}
```

## Advanced Design Patterns

### Computed Pattern Implementation

The database implements the **Computed Pattern** to pre-calculate frequently accessed statistics, improving query performance and reducing real-time computation overhead.

#### Event Computed Statistics
Events include `computedStats` with pre-calculated metrics:
- **`totalTicketsSold`**: Sum of all sold tickets across tiers
- **`totalRevenue`**: Calculated revenue from ticket sales
- **`attendanceRate`**: Percentage of capacity filled
- **`reviewCount`**: Number of reviews received
- **`averageRating`**: Average review rating
- **`lastUpdated`**: Timestamp of last calculation

#### Venue Computed Statistics
Venues include `computedStats` with performance metrics:
- **`totalEventsHosted`**: Number of events at this venue
- **`averageAttendance`**: Average attendance per event
- **`revenueGenerated`**: Total revenue from events
- **`lastEventDate`**: Most recent event date
- **`lastUpdated`**: Timestamp of last calculation

#### Benefits of Computed Pattern
- **Performance**: Eliminates expensive aggregations for dashboard queries
- **Consistency**: Single source of truth for statistics
- **Scalability**: Reduces database load during peak usage
- **Real-time Updates**: Statistics updated via application triggers

#### Update Triggers
Statistics are recalculated when:
- Tickets are sold/refunded
- Reviews are added/updated
- Events are created/completed
- Check-ins occur

### Bucket Pattern for Time-Series Data

The **Bucket Pattern** is implemented for analytics and time-series data:

#### Event Analytics Buckets
```javascript
{
  "_id": ObjectId,
  "bucket_type": "daily_analytics",
  "date": ISODate("2024-01-15"),
  "events": {
    "total_created": 25,
    "by_category": {
      "Technology": 8,
      "Music": 12,
      "Sports": 5
    },
    "byType": {
      "inPerson": 15,
      "virtual": 7,
      "hybrid": 3
    }
  },
  "attendance": {
    "totalCheckins": 1250,
    "averagePerEvent": 50
  },
  "revenue": {
    "totalGenerated": 15750.00,
    "currency": "USD"
  }
}
```

#### Benefits
- **Reduced Indexes**: Single document per time period
- **Faster Queries**: Pre-aggregated data for dashboards
- **Storage Efficiency**: Compressed time-series data
- **Analytics Ready**: Direct aggregation support

### Extended Reference Pattern

The **Extended Reference Pattern** is implemented for frequently accessed venue data in events:

#### Event-Venue References
Events store denormalized venue data for performance:
```javascript
{
  "venueId": ObjectId("..."),
  "venue_reference": {          // Extended reference data
    "name": "Convention Center",
    "city": "San Francisco", 
    "capacity": 5000,
    "venueType": "conferenceCenter"
  }
}
```

#### Benefits
- **Query Performance**: Avoid joins for event listings and venue filtering
- **Reduced Lookups**: Venue name/city available in event queries without additional database calls
- **Consistency**: Reference data updated via application logic when venue changes
- **Filtering**: Enable venue-based filtering without joins (e.g., "events at conference centers")

#### Update Strategy
Extended reference data is updated when:
- Venue name, city, capacity, or type changes
- Event is created with a venue
- Venue data is modified (via application triggers)

## Polymorphic Design & Schema Versioning

### Polymorphic Design Strategy

The database implements polymorphic design patterns for both `events` and `venues` collections, allowing different types of entities to have specialized attributes while maintaining a common base structure.

#### Event Polymorphism
Events support four distinct types with type-specific attributes:

- **`inPerson`**: Traditional physical events at venues
- **`virtual`**: Online-only events with virtual meeting details
- **`hybrid`**: Events with both physical and virtual components
- **`recurring`**: Events that repeat on a schedule

**Discriminator Field**: `eventType` determines which polymorphic fields are populated
**Type-Specific Fields**:
- `virtualDetails`: Platform, meeting URL, recording availability
- `hybridDetails`: Separate capacities and virtual meeting URL
- `recurringDetails`: Frequency, end date, exception dates

#### Venue Polymorphism
Venues support six distinct types with specialized attributes:

- **`conferenceCenter`**: Meeting rooms, exhibition space, AV equipment
- **`park`**: Outdoor spaces with activities and permit requirements
- **`restaurant`**: Dining venues with menu and reservation details
- **`virtualSpace`**: Online platforms with participant limits
- **`stadium`**: Large venues with seating and event facilities
- **`theater`**: Performance venues with stage and seating details

**Discriminator Field**: `venueType` determines which polymorphic fields are populated
**Type-Specific Fields**:
- `conferenceCenterDetails`: Meeting rooms, exhibition space, catering
- `parkDetails`: Park type, activities, permits, seasonal hours
- `virtualSpaceDetails`: Platform, participant limits, recording capability

### Schema Versioning Strategy

All collections include a `schemaVersion` field to support future schema evolution:

- **Current Version**: "1.0" for all collections
- **Migration Support**: Version field enables gradual schema updates
- **Backward Compatibility**: Legacy data remains accessible during transitions
- **Validation**: JSON Schema validation includes version-specific rules

**Benefits**:
- **Safe Evolution**: Add new fields without breaking existing data
- **Gradual Migration**: Update documents in batches by version
- **Rollback Capability**: Revert to previous schema if needed
- **Analytics**: Track adoption of new schema versions

### Polymorphic Query Examples

```javascript
// Find all virtual events
db.events.find({ eventType: "virtual" })

// Find conference centers with meeting rooms
db.venues.find({ 
  venueType: "conferenceCenter",
  "conferenceCenterDetails.meetingRooms": { $gt: 5 }
})

// Find hybrid events with virtual capacity
db.events.find({ 
  eventType: "hybrid",
  "hybridDetails.virtualCapacity": { $gt: 100 }
})

// Find recurring events ending this year
db.events.find({
  eventType: "recurring",
  "recurringDetails.endRecurrence": { $gte: ISODate("2024-01-01") }
})
```

### Schema Versioning Query Examples

```javascript
// Find all documents using schema version 1.0
db.events.find({ schemaVersion: "1.0" })

// Count documents by schema version
db.events.aggregate([
  { $group: { _id: "$schemaVersion", count: { $sum: 1 } } }
])

// Find documents that need migration (older versions)
db.events.find({ schemaVersion: { $ne: "1.0" } })
```

## Schema Validation & Relationships

### Document Relationships Strategy

#### Embedding vs Referencing
- **Embedded Documents** (for frequently accessed, tightly bound data):
  - `tickets[]` in events - always displayed together
  - `attendees[]` in events - quick RSVP display
  - `address` in venues - always needed with venue info

- **Referenced Documents** (for large or shared data):
  - `venueId` in events - venues shared across multiple events
  - `userId` in checkins - users referenced across many events
  - `eventId` in checkins - events referenced by many check-ins

#### Bridge Table Design: Check-ins Collection
The `checkins` collection serves as a **bridge table** (also called an association table or join table) that creates a many-to-many relationship between users and events. This design pattern offers several advantages:

**Why a Separate Collection?**
- **Analytics Flexibility**: Easy to query attendance patterns, user behavior, and venue statistics
- **Query Performance**: Optimized indexes for common analytics queries without complex joins
- **Scalability**: Avoids document size bloat in user or event collections
- **Data Integrity**: Centralized check-in logic with consistent validation rules

**Common Analytics Queries Enabled:**
- "Which users attended events at this venue last month?"
- "What's the average check-in time for this event type?"
- "How many repeat attendees do we have?"
- "Which events have the highest attendance rates?"

**Denormalization Strategy:**
- `venueId` is denormalized (duplicated) in check-ins for analytics performance
- This avoids expensive joins when analyzing venue-specific attendance data
- Trade-off: Slight storage overhead for significant query performance gains

### Schema Validation Rules

All collections enforce comprehensive JSON Schema validation with the following key features:

#### Coordinate Bounds Validation
- **Longitude**: Must be between -180 and 180 degrees
- **Latitude**: Must be between -90 and 90 degrees
- **GeoJSON Structure**: All location fields must be valid GeoJSON Point objects
- **Coordinate Arrays**: Must contain exactly 2 elements [longitude, latitude]

#### Required Fields Enforcement
- **Events**: `title`, `category`, `eventType`, `schemaVersion`, `location`, `startDate`, `createdAt`, `updatedAt`
- **Venues**: `name`, `venueType`, `schemaVersion`, `location`, `address`, `createdAt`
- **Users**: `email`, `schemaVersion`, `profile`, `createdAt`
- **Checkins**: `eventId`, `userId`, `venueId`, `checkInTime`, `qrCode`, `schemaVersion`, `createdAt`
- **Reviews**: `userId`, `rating`, `schemaVersion`, `createdAt`, `updatedAt` (plus either `eventId` OR `venueId`)

#### Data Type and Range Validation
- **String Lengths**: Enforced min/max lengths for all text fields
- **Numeric Ranges**: Positive values for counts, prices, and capacities
- **Email Format**: Valid email pattern for user accounts
- **Date Logic**: End dates must be after start dates
- **Array Constraints**: Proper array structures for coordinates and tags
- **Rating Bounds**: Reviews rating must be between 1 and 5 (inclusive)
- **Review Logic**: Either `eventId` OR `venueId` must be provided, not both

#### Example: Events Collection Validation
```javascript
{
  $jsonSchema: {
    bsonType: "object",
    required: ["title", "category", "eventType", "schemaVersion", "location", "startDate", "createdAt", "updatedAt"],
    properties: {
      title: {
        bsonType: "string",
        minLength: 1,
        maxLength: 200
      },
      eventType: {
        enum: ["inPerson", "virtual", "hybrid", "recurring"]
      },
      schemaVersion: {
        enum: ["1.0"]
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
      startDate: { bsonType: "date" },
      maxAttendees: { bsonType: "int", minimum: 1 },
      virtualDetails: {
        bsonType: "object",
        properties: {
          platform: { bsonType: "string" },
          meetingUrl: { bsonType: "string" },
          recordingAvailable: { bsonType: "bool" },
          timezone: { bsonType: "string" }
        }
      },
      hybridDetails: {
        bsonType: "object",
        properties: {
          virtualCapacity: { bsonType: "int", minimum: 0 },
          inPersonCapacity: { bsonType: "int", minimum: 0 },
          virtualMeetingUrl: { bsonType: "string" }
        }
      },
      recurringDetails: {
        bsonType: "object",
        properties: {
          frequency: { enum: ["daily", "weekly", "monthly", "yearly"] },
          endRecurrence: { bsonType: "date" },
          exceptions: {
            bsonType: "array",
            items: { bsonType: "date" }
          }
        }
      }
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
db.events.createIndex({"startDate": 1})
db.events.createIndex({"createdAt": 1})
```
**Purpose**: Efficient date range queries and sorting
**Queries**: Upcoming events, date filtering, chronological sorting

### 4. Polymorphic Indexes
```javascript
// Event type + Date filtering
db.events.createIndex({"eventType": 1, "startDate": 1})

// Event type + Category filtering
db.events.createIndex({"eventType": 1, "category": 1})

// Venue type + Capacity filtering
db.venues.createIndex({"venueType": 1, "capacity": 1})

// Venue type + Rating filtering
db.venues.createIndex({"venueType": 1, "rating": 1})

// Schema version filtering
db.events.createIndex({"schemaVersion": 1})
db.venues.createIndex({"schemaVersion": 1})
```
**Purpose**: Optimize polymorphic queries and schema version filtering
**Queries**: "Virtual events this month", "Conference centers with high capacity"

### 5. Compound Indexes for Common Query Patterns
```javascript
// Category + Date filtering
db.events.createIndex({"category": 1, "startDate": 1})

// Geospatial + Date filtering  
db.events.createIndex({"location": "2dsphere", "startDate": 1})

// Organizer + Date filtering
db.events.createIndex({"organizer": 1, "startDate": 1})

// Analytics queries
db.events.createIndex({"category": 1, "createdAt": 1})
db.events.createIndex({"startDate": 1, "category": 1})
```
**Purpose**: Optimize compound queries without index intersection
**Queries**: "Tech events this weekend", "Events near me next month"

### 6. Cursor-based Pagination Support
```javascript
db.events.createIndex({"_id": 1, "startDate": 1})
```
**Purpose**: Efficient cursor-based pagination
**Queries**: Large result set pagination without performance degradation

### 7. Array and Filtering Indexes
```javascript
db.events.createIndex({"tags": 1})        // Tag filtering
db.events.createIndex({"maxAttendees": 1}) // Capacity filtering
db.events.createIndex({"endDate": 1})     // End date queries
```
**Purpose**: Support filtering and aggregation queries
**Queries**: Events by tags, capacity-based filtering

### 8. Reviews Collection Indexes
```javascript
db.reviews.createIndex({"eventId": 1})     // Reviews by event
db.reviews.createIndex({"venueId": 1})     // Reviews by venue
db.reviews.createIndex({"userId": 1})      // Reviews by user
db.reviews.createIndex({"rating": 1})       // Rating-based queries
db.reviews.createIndex({"createdAt": 1})   // Chronological sorting
db.reviews.createIndex({"eventId": 1, "rating": 1}) // Event rating aggregation
db.reviews.createIndex({"venueId": 1, "rating": 1}) // Venue rating aggregation
```
**Purpose**: Support review queries and aggregations
**Queries**: Reviews by event/venue, rating statistics, user review history

### 9. Check-ins Collection Indexes
```javascript
db.checkins.createIndex({"eventId": 1})           // Check-ins by event
db.checkins.createIndex({"userId": 1})            // User attendance history
db.checkins.createIndex({"venueId": 1})           // Venue attendance analytics
db.checkins.createIndex({"checkInTime": 1})      // Time-based analytics
db.checkins.createIndex({"qrCode": 1})            // Unique QR code lookups
db.checkins.createIndex({"eventId": 1, "userId": 1}) // Prevent duplicate check-ins
db.checkins.createIndex({"venueId": 1, "checkInTime": 1}) // Venue time analytics
db.checkins.createIndex({"userId": 1, "checkInTime": 1}) // User attendance patterns
```
**Purpose**: Support attendance analytics and prevent duplicate check-ins
**Queries**: Attendance tracking, user patterns, venue statistics, duplicate prevention

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

### 3. Polymorphic Queries
```javascript
// Find all virtual events this month
db.events.find({
  "eventType": "virtual",
  "startDate": { $gte: startOfMonth, $lte: endOfMonth }
})

// Find conference centers with high capacity
db.venues.find({
  "venueType": "conferenceCenter",
  "capacity": { $gt: 500 }
})

// Find hybrid events with virtual capacity
db.events.find({
  "eventType": "hybrid",
  "hybridDetails.virtualCapacity": { $gt: 100 }
})

// Find recurring events ending this year
db.events.find({
  "eventType": "recurring",
  "recurringDetails.endRecurrence": { $gte: ISODate("2024-01-01") }
})
```
**Index Used**: `{"eventType": 1, "startDate": 1}`, `{"venueType": 1, "capacity": 1}`
**Performance**: O(log n) with polymorphic filtering

### 4. Compound Queries
```javascript
// Tech events this weekend near location
db.events.find({
  "category": "Technology",
  "startDate": { $gte: friday, $lte: sunday },
  "location": {
    $near: {
      $geometry: { type: "Point", coordinates: [lng, lat] },
      $maxDistance: 50000
    }
  }
})
```
**Index Used**: `{"location": "2dsphere", "startDate": 1}`
**Performance**: Single index scan, very efficient

### 5. Cursor-based Pagination
```javascript
// First page
db.events.find().sort({"_id": 1}).limit(50)

// Next page using cursor
db.events.find({"_id": {$gt: lastId}}).sort({"_id": 1}).limit(50)
```
**Index Used**: `{"_id": 1, "startDate": 1}`
**Performance**: O(log n) regardless of page number

### 6. Analytics Aggregations
```javascript
// Peak event times
db.events.aggregate([
  {
    $group: {
      _id: {
        hour: { $hour: "$startDate" },
        dayOfWeek: { $dayOfWeek: "$startDate" }
      },
      count: { $sum: 1 }
    }
  },
  { $sort: { count: -1 } }
])
```
**Index Used**: `{"startDate": 1}`
**Performance**: Efficient with proper date indexing

### 7. Reviews Queries
```javascript
// Get reviews for a specific event
db.reviews.find({"eventId": ObjectId("...")}).sort({"createdAt": -1})

// Get average rating for an event
db.reviews.aggregate([
  { $match: { "eventId": ObjectId("...") } },
  { $group: { _id: null, avgRating: { $avg: "$rating" }, count: { $sum: 1 } } }
])

// Get user's review history
db.reviews.find({"userId": ObjectId("...")}).sort({"createdAt": -1})

// Get top-rated events by average review score
db.reviews.aggregate([
  { $group: { _id: "$eventId", avgRating: { $avg: "$rating" }, count: { $sum: 1 } } },
  { $match: { count: { $gte: 5 } } }, // Minimum 5 reviews
  { $sort: { avgRating: -1 } }
])
```
**Index Used**: `{"eventId": 1}`, `{"userId": 1}`, `{"eventId": 1, "rating": 1}`
**Performance**: O(log n) with proper indexing

### 8. Check-ins Analytics Queries
```javascript
// Get all check-ins for an event
db.checkins.find({"eventId": ObjectId("...")}).sort({"checkInTime": -1})

// Get user's attendance history
db.checkins.find({"userId": ObjectId("...")}).sort({"checkInTime": -1})

// Get venue attendance statistics
db.checkins.aggregate([
  { $match: { "venueId": ObjectId("...") } },
  { $group: { 
    _id: { $dateToString: { format: "%Y-%m", date: "$checkInTime" } },
    totalCheckins: { $sum: 1 },
    uniqueUsers: { $addToSet: "$userId" }
  }},
  { $project: { 
    month: "$_id", 
    totalCheckins: 1, 
    uniqueUsers: { $size: "$uniqueUsers" }
  }}
])

// Find repeat attendees (users who attended multiple events)
db.checkins.aggregate([
  { $group: { _id: "$userId", eventCount: { $sum: 1 }, events: { $addToSet: "$eventId" } } },
  { $match: { eventCount: { $gte: 2 } } },
  { $sort: { eventCount: -1 } }
])

// Check-in time patterns (peak check-in hours)
db.checkins.aggregate([
  { $group: { 
    _id: { $hour: "$checkInTime" }, 
    count: { $sum: 1 } 
  }},
  { $sort: { count: -1 } }
])
```
**Index Used**: `{"eventId": 1}`, `{"userId": 1}`, `{"venueId": 1}`, `{"checkInTime": 1}`
**Performance**: O(log n) with proper indexing

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
- **Reviews queries**: < 30ms
- **Review aggregations**: < 100ms
- **Check-ins queries**: < 25ms
- **Attendance analytics**: < 150ms
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
- **Horizontal Scaling**: Sharding by geography (`location`) or time (`startDate`)
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
- 📋 Reviews and ratings system

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
