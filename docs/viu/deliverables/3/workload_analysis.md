# B. Workload & Operations Analysis for EventSphere

## Most Common Database Operations

| Operation | Type | Criticality | Frequency | Target Collection(s) |
|-----------|------|-------------|-----------|----------------------|
| Event discovery near a location (with optional date/category filters) | Read | High | Many per minute | events |
| Full-text event search | Read | High | Many per minute | events |
| Filter events by type (virtual/in-person/hybrid/recurring) | Read | High | Many per minute | events |
| User check-in (prevent duplicates) | Write | High | Many per minute (during events) | checkins |
| Fetch reviews for an event/venue | Read | Medium | Several per minute | reviews |
| Venue discovery near a location | Read | Medium | Several per minute | venues |
| User login by email | Read | High | Many per minute | users |
| Attendance analytics by venue/time | Aggregate | Medium | Few per hour | checkins |
| User attendance history | Read | Medium | Several per minute | checkins |
| Event updates (CRUD) | Update/Write | Medium | Several per minute | events |

## Why these operations are indexed

- Event discovery: 2dsphere on `events.location` and a compound `{category, startDate}` so map + date/category filters stay fast.
- Full-text search: Text index on `events.title, description, category, tags` to surface relevant results with one query.
- Event type filters: `{eventType, startDate}` to pair the discriminator with the common date window.
- Check-ins: Unique `{eventId, userId}` to hard‑stop duplicates at write time.
- Reviews: `{eventId}`, `{venueId}`, and `{eventId, rating}` to load reviews quickly and support averages.
- Venues: 2dsphere on `venues.location` for “near me”, plus `{venueType, capacity}` for selection flows.
- Users: Unique `{email}` for quick login lookups; `{lastLogin}` and `{createdAt}` for simple reporting.