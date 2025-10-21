# A. Indexing Strategy & Justification for EventSphere

## 2. Index Summary Table

| Collection | Index Key(s) | Type | Purpose / Query Supported | 
|------------|--------------|------|---------------------------|
| **events** | `location` | 2dsphere | Geospatial queries ($geoNear, $near) |
| **events** | `title, description, category, tags` | Text | Full-text search with relevance scoring |
| **events** | `category, startDate` | Compound | Category + date filtering |
| **events** | `eventType, startDate` | Compound | Polymorphic event type filtering |
| **venues** | `location` | 2dsphere | Geospatial venue discovery |
| **venues** | `venueType, capacity` | Compound | Polymorphic venue filtering |
| **venues** | `name, description, amenities, address.city` | Text | Full-text venue search |
| **venues** | `venueType, rating` | Compound | Venue type + rating filtering |
| **reviews** | `eventId` | Single field | Reviews by event |
| **reviews** | `venueId` | Single field | Reviews by venue |
| **reviews** | `eventId, rating` | Compound | Event rating aggregations |
| **reviews** | `userId` | Single field | User review history |
| **checkins** | `eventId, userId` | Compound (Unique) | Prevent duplicate check-ins |
| **checkins** | `eventId` | Single field | Check-ins by event |
| **checkins** | `userId` | Single field | User attendance history |
| **checkins** | `venueId, checkInTime` | Compound | Venue time analytics |
| **users** | `email` | Single field (Unique) | User authentication |
| **users** | `createdAt` | Single field | User registration analytics |
| **users** | `lastLogin` | Single field | Active user identification |
| **users** | `profile.preferences.location` | 2dsphere | Location-based user discovery |

## 3. Index Creation Script
 The attached `create_indexes.js` file contains the index creation script.

## 4. Index Reasoning

### 1. Geospatial Indexes (2dsphere)

**Events Collection - Location Index**
- **Query Pattern**: Find events within X km of user location
- **Frequency**: Very High (primary discovery feature)
- **Why this index type**: 2dsphere supports spherical distance queries on GeoJSON points, enabling $near/$geoNear for the map-based discovery I'd like to implement on a frontend, as described in the proposal and design docs.

**Venues Collection - Location Index**
- **Query Pattern**: Find venues near event location or user location
- **Frequency**: High (venue discovery and event creation)
- **Why this index type**: 2dsphere is required for distance queries on venues' GeoJSON points, matching the way events are created and venues are selected.

### 2. Text Search Indexes

**Events Collection - Multi-field Text Index**
- **Query Pattern**: Full-text search across title, description, category, and tags
- **Frequency**: Very High (primary search functionality)
- **Why this index type**: Text index provides tokenization, stemming, and relevance scoring across multiple fields, aligning with the full-text search requirement.

**Venues Collection - Multi-field Text Index**
- **Query Pattern**: Full-text search across venue name, description, amenities, and city
- **Frequency**: High (venue discovery and search functionality)
- **Why this index type**: Text index lets users find venues by name, amenities, and city in a single search, which is superior to multiple regex filters.

### 3. Compound Indexes for Common Query Patterns

**Category + Date Filtering**
- **Query Pattern**: "Technology events this weekend"
- **Frequency**: Very High (most common user filter)
- **Why this index type**: Compound index `{category: 1, startDate: 1}` supports equality on category and efficient range/sort on date consistent with discovery UI.

**Geospatial + Date Filtering**
- **Query Pattern**: "Events near me next month"
- **Frequency**: High (location + time filtering)
- **Why this index type**: Combining `location` (2dsphere) with `startDate` in a compound index supports geo filtering with a time window in a single index path when needed.

### 4. Polymorphic Indexes

**Event Type Filtering**
- **Query Pattern**: Filter by event type (virtual, hybrid, in-person, recurring)
- **Frequency**: High (event type is a primary discriminator)
- **Indexes**: 
  - `{eventType: 1, startDate: 1}` - Type + date filtering
  - `{eventType: 1, category: 1}` - Type + category filtering
- **Why this index type**: Compound indexes align to polymorphic queries in the architecture, enabling selective filtering on the discriminator with a secondary field.

**Venue Type Filtering**
- **Query Pattern**: "Conference centers with high capacity"
- **Frequency**: Medium (venue selection and filtering)
- **Indexes**:
  - `{venueType: 1, capacity: 1}` - Type + capacity filtering
  - `{venueType: 1, rating: 1}` - Type + quality filtering
- **Why this index type**: Compound indexes on `venueType` plus a numeric field support the most common admin/user filters without requiring multiple single-field scans.

### 5. Extended Reference Pattern Indexes

**Venue Reference Optimization**
- **Query Pattern**: Filter events by venue type or city without joins
- **Frequency**: Medium (venue-based filtering)
- **Indexes**:
  - `{venueReference.venueType: 1, startDate: 1}` - Venue type + date
  - `{venueReference.city: 1, startDate: 1}` - City + date
  - `{venueReference.capacity: 1}` - Capacity sorting
- **Why this index type**: These compound indexes on the denormalized venue reference fields make it easy to filter events by venue details right inside the events collection, so there's no need to join or look up in the `venues` collection.

### 6. Analytics and Aggregation Indexes

**Reviews Aggregation**
- **Query Pattern**: Calculate average ratings per event/venue
- **Frequency**: High (rating calculations)
- **Indexes**:
  - `{eventId: 1, rating: 1}` - Event rating aggregations
  - `{venueId: 1, rating: 1}` - Venue rating aggregations
- **Why this index type**: These compund indexes support rating calculations and aggregations.

**Check-ins Analytics**
- **Query Pattern**: Attendance patterns, peak hours, user behavior
- **Frequency**: High (analytics and reporting)
- **Indexes**:
  - `{venueId: 1, checkInTime: 1}` - Venue time analytics
  - `{userId: 1, checkInTime: 1}` - User attendance patterns
- **Why this index type**: These compound indexes support attendance patterns and user behavior analytics.

### 7. Data Integrity Indexes

**Duplicate Prevention**
- **Query Pattern**: Prevent duplicate check-ins per user/event
- **Frequency**: High (data integrity)
- **Index**: `{eventId: 1, userId: 1}` (Unique)
- **Why this index type**: This unique compound index prevents duplicate check-ins per user/event at write time.