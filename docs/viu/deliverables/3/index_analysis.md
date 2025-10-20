# Index Analysis & Justification for EventSphere - Optimized (4 per Collection)

## Index Summary Table

| Collection | Index Key(s) | Type | Purpose / Query Supported | Frequency | Justification |
|------------|--------------|------|---------------------------|-----------|---------------|
| **events** | `location` | 2dsphere | Geospatial queries ($geoNear, $near) | High | Core feature for event discovery within radius |
| **events** | `title, description, category, tags` | Text | Full-text search with relevance scoring | High | Primary search functionality across multiple fields |
| **events** | `category, startDate` | Compound | Category + date filtering | High | Common user filter combination |
| **events** | `eventType, startDate` | Compound | Polymorphic event type filtering | High | Filter by event type (virtual, hybrid, etc.) |
| **venues** | `location` | 2dsphere | Geospatial venue discovery | High | Find venues near location |
| **venues** | `venueType, capacity` | Compound | Polymorphic venue filtering | Medium | Filter venues by type and capacity |
| **venues** | `venueType, rating` | Compound | Venue type + rating filtering | Medium | Quality-based venue selection |
| **venues** | `venueType` | Single field | Basic venue type filtering | Medium | Fallback for simple type queries |
| **reviews** | `eventId` | Single field | Reviews by event | High | Display reviews for specific events |
| **reviews** | `venueId` | Single field | Reviews by venue | High | Display reviews for specific venues |
| **reviews** | `eventId, rating` | Compound | Event rating aggregations | High | Calculate average ratings per event |
| **reviews** | `userId` | Single field | User review history | Medium | User profile and history |
| **checkins** | `eventId, userId` | Compound (Unique) | Prevent duplicate check-ins | High | Data integrity constraint |
| **checkins** | `eventId` | Single field | Check-ins by event | High | Event attendance tracking |
| **checkins** | `userId` | Single field | User attendance history | High | User profile and analytics |
| **checkins** | `venueId, checkInTime` | Compound | Venue time analytics | Medium | Venue-specific temporal analysis |
| **users** | `email` | Single field (Unique) | User authentication | High | Critical for login operations |
| **users** | `createdAt` | Single field | User registration analytics | Medium | User growth analysis |
| **users** | `lastLogin` | Single field | Active user identification | Medium | User engagement metrics |
| **users** | `profile.preferences.location` | 2dsphere | Location-based user discovery | Low | Recommendation engine support |

## Optimization Strategy

### Index Reduction Rationale

The original comprehensive index strategy included 32+ indexes across all collections. This has been optimized to exactly 4 indexes per collection (20 total) based on:

1. **Query Frequency Analysis**: Focus on high-frequency, critical operations
2. **Compound Index Efficiency**: Single indexes supporting multiple query patterns
3. **Storage Optimization**: 35% reduction in index count while maintaining performance
4. **Performance Focus**: Prioritize user-facing operations over nice-to-have features

### Removed Indexes Justification

**Events Collection (12 → 4 indexes)**:
- Removed single-field indexes replaced by compound indexes
- Removed low-frequency analytics indexes
- Removed extended reference pattern indexes (less critical than core patterns)
- Removed pagination indexes (can use `_id` for cursor pagination)

**Venues Collection (5 → 4 indexes)**:
- Consolidated venue type filtering into compound indexes
- Removed single-field capacity and rating indexes
- Added basic venue type index for fallback queries

**Reviews Collection (7 → 4 indexes)**:
- Kept high-frequency event and venue review indexes
- Removed single-field rating and createdAt indexes
- Removed venue rating aggregation (lower frequency than event reviews)

**Checkins Collection (8 → 4 indexes)**:
- Kept critical duplicate prevention and attendance tracking
- Removed QR code index (can use eventId + userId for lookups)
- Removed user time analytics (lower frequency than venue analytics)

**Users Collection (3 → 4 indexes)**:
- Added essential indexes for user management and analytics
- Maintained authentication and location-based features

## Detailed Index Justification

### 1. Geospatial Indexes (2dsphere)

**Events Collection - Location Index**
- **Query Pattern**: Find events within X km of user location
- **Frequency**: Very High (primary discovery feature)
- **Performance Impact**: O(log n) - Excellent for large datasets
- **Example Query**:
  ```javascript
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

**Venues Collection - Location Index**
- **Query Pattern**: Find venues near event location or user location
- **Frequency**: High (venue discovery and event creation)
- **Performance Impact**: O(log n) - Essential for location-based features

### 2. Text Search Indexes

**Events Collection - Multi-field Text Index**
- **Query Pattern**: Full-text search across title, description, category, and tags
- **Frequency**: Very High (primary search functionality)
- **Performance Impact**: O(log n) with relevance scoring
- **Example Query**:
  ```javascript
  db.events.find(
    { $text: { $search: "technology conference" } },
    { score: { $meta: "textScore" } }
  ).sort({ score: { $meta: "textScore" } })
  ```

### 3. Compound Indexes for Common Query Patterns

**Category + Date Filtering**
- **Query Pattern**: "Technology events this weekend"
- **Frequency**: Very High (most common user filter)
- **Index**: `{category: 1, startDate: 1}`
- **Performance**: Single index scan, very efficient

**Geospatial + Date Filtering**
- **Query Pattern**: "Events near me next month"
- **Frequency**: High (location + time filtering)
- **Index**: `{location: "2dsphere", startDate: 1}`
- **Performance**: Single index scan with geospatial optimization

### 4. Polymorphic Indexes

**Event Type Filtering**
- **Query Pattern**: Filter by event type (virtual, hybrid, in-person, recurring)
- **Frequency**: High (event type is a primary discriminator)
- **Indexes**: 
  - `{eventType: 1, startDate: 1}` - Type + date filtering
  - `{eventType: 1, category: 1}` - Type + category filtering
- **Performance**: O(log n) with polymorphic support

**Venue Type Filtering**
- **Query Pattern**: "Conference centers with high capacity"
- **Frequency**: Medium (venue selection and filtering)
- **Indexes**:
  - `{venueType: 1, capacity: 1}` - Type + capacity filtering
  - `{venueType: 1, rating: 1}` - Type + quality filtering

### 5. Extended Reference Pattern Indexes

**Venue Reference Optimization**
- **Query Pattern**: Filter events by venue type or city without joins
- **Frequency**: Medium (venue-based filtering)
- **Indexes**:
  - `{venueReference.venueType: 1, startDate: 1}` - Venue type + date
  - `{venueReference.city: 1, startDate: 1}` - City + date
  - `{venueReference.capacity: 1}` - Capacity sorting
- **Performance**: Avoids expensive joins for venue-based queries

### 6. Analytics and Aggregation Indexes

**Reviews Aggregation**
- **Query Pattern**: Calculate average ratings per event/venue
- **Frequency**: High (rating calculations)
- **Indexes**:
  - `{eventId: 1, rating: 1}` - Event rating aggregations
  - `{venueId: 1, rating: 1}` - Venue rating aggregations
- **Performance**: Optimized for aggregation pipelines

**Check-ins Analytics**
- **Query Pattern**: Attendance patterns, peak hours, user behavior
- **Frequency**: High (analytics and reporting)
- **Indexes**:
  - `{venueId: 1, checkInTime: 1}` - Venue time analytics
  - `{userId: 1, checkInTime: 1}` - User attendance patterns
- **Performance**: Efficient temporal analysis

### 7. Data Integrity Indexes

**Duplicate Prevention**
- **Query Pattern**: Prevent duplicate check-ins per user/event
- **Frequency**: High (data integrity)
- **Index**: `{eventId: 1, userId: 1}` (Unique)
- **Performance**: O(log n) uniqueness constraint

### 8. Pagination Support Indexes

**Cursor-based Pagination**
- **Query Pattern**: Efficient pagination for large result sets
- **Frequency**: High (user interface pagination)
- **Index**: `{_id: 1, startDate: 1}`
- **Performance**: O(log n) regardless of page number

## Index Performance Characteristics

### Expected Performance (10,000+ events)
- **Geospatial queries**: < 50ms
- **Text search**: < 100ms
- **Compound queries**: < 75ms
- **Pagination**: < 25ms (cursor-based)
- **Analytics aggregations**: < 200ms
- **Review queries**: < 30ms
- **Check-in queries**: < 25ms

### Index Size Estimates
- **Geospatial indexes**: ~15% of collection size
- **Text indexes**: ~20% of collection size
- **Compound indexes**: ~10% of collection size
- **Single field indexes**: ~5% of collection size
- **Total index overhead**: ~50% of collection size

### Memory Usage
- **Indexes cached in RAM**: Essential for performance
- **Working set**: Indexes + frequently accessed documents
- **Memory allocation**: 60% for indexes, 40% for data

## Index Maintenance and Monitoring

### Index Usage Statistics
```javascript
// Monitor index usage
db.events.aggregate([{ $indexStats: {} }])

// Check index utilization
db.events.getIndexes()
```

### Index Optimization Recommendations
1. **Monitor slow queries**: Use MongoDB profiler to identify unindexed queries
2. **Index intersection**: Avoid when compound indexes are more efficient
3. **Partial indexes**: Consider for frequently filtered subsets
4. **TTL indexes**: For time-based data cleanup
5. **Sparse indexes**: For optional fields with high selectivity

### Future Index Considerations
1. **Sharding**: Indexes will be distributed across shards
2. **Compound index order**: Optimize for most selective fields first
3. **Index intersection**: May be more efficient than large compound indexes
4. **Covered queries**: Include all projected fields in indexes when possible
