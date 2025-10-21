# C. Design Patterns Used & Anti-Patterns Avoided for EventSphere

## Design Patterns Used

### 1. Extended Reference Pattern

**Why this pattern was used**: Events store denormalized venue data for easier querying of venue details.

```javascript
// Event document with extended venue reference
{
  "_id": ObjectId("..."),
  "title": "Tech Conference 2024",
  "venueId": ObjectId("venue..."),
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
- **Query Performance**: Avoids joins when filtering events by venue type or city
- **Reduced Lookups**: Venue information is available in event queries without additional database calls
- **Better User Experience**: Event listings show venue details immediately without extra queries

### 2. Computed Pattern

**Why this pattern was used**: Pre-calculated statistics stored in documents to improve query performance and provide a single source of truth for statistics.

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
- **Real-time Updates**: Statistics updated via application triggers

**When stats are updated**:
- Tickets are sold/refunded
- Reviews are added/updated
- Events are created/completed
- Check-ins happen

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

---

## Anti-Patterns Avoided

### 1. Bloated Documents

**Anti-Pattern**: Storing large, too much data in a single document.

**Why I avoided this anti-pattern**:
- **Document Size Limit**: MongoDB has 16MB document size limit
- **Write Performance**: Updating user document becomes expensive
- **Memory Usage**: Large documents consume excessive RAM, and make for less efficient queries.
- **Query Performance**: Filtering embedded arrays is inefficient, making it harder to query reviews.

**My Solution**: Separate `reviews` collection with references to `users` and `events`.

### 2. Over-Indexing

**Anti-pattern**: Creating indexes for every possible query without considering write performance.

**What I did wrong initially**: I had 30+ indexes across all collections, including single-field indexes on every possible filter field.

**Why this was bad**:
- **Write Performance**: Each index slows down insert/update operations
- **Storage Overhead**: Index storage was larger than data storage
- **Memory Usage**: Too many indexes consumed excessive RAM

**My solution**: Reduced to 4 indexes per collection, focusing on compound indexes that support multiple query patterns.

### 3. Over-Embedding Large Subdocuments

**Anti-pattern**: Storing large arrays or subdocuments that grow unbounded.

**Why I avoided this**: Instead of embedding all user check-ins in the `users` collection, I created a separate `checkins` collection.

**What would have been bad**:
- **Document Size**: User documents would grow indefinitely with each check-in
- **Write Performance**: Updating a user document becomes slower as it grows
- **Query Performance**: Filtering embedded arrays is inefficient

**My solution**: Separate `checkins` collection with references to `users` and `events`, enabling efficient analytics queries without bloating user documents.