# Linear Backlog – Mongo Events Demo (32 tickets)

This is a living backlog to drive end-to-end delivery. Tickets are grouped by phases and include acceptance criteria (AC), estimates, and dependencies (Deps).

Legend: P = priority (1 highest), E = estimate (ideal hours), L = labels

---

## Phase 1 – Foundations (Schema, Indexes, CRUD)

**EVE-5** Schema finalization and validation
- P:1  E:4h  L:database,schema
- Status: ✅ COMPLETED
- Desc: Finalize `events`, `venues`, `users`, `checkins` schemas with JSON Schema validation.
- AC:
  - Events collection enforces required fields and GeoJSON structure
  - Coordinate bounds validated
  - `DATABASE_DESIGN.md` matches implemented schema

**EVE-6** Index suite implementation in app/database.py
- P:1  E:3h  L:indexing,performance
- Status: ✅ COMPLETED
- Desc: Ensure all indexes exist: 2dsphere, text, start_date, category+start_date, location+start_date, organizer+start_date, created_at, tags.
- AC:
  - `list_indexes` shows all specified indexes
  - Index build idempotent at startup
- Deps: EVE-5

**EVE-7** CRUD services parity and unit tests
- P:1  E:4h  L:backend,testing
- Status: ✅ COMPLETED
- Desc: Verify create/get/update/delete paths and add unit tests.
- AC:
  - Tests cover happy-path and invalid ObjectId
  - Update respects partial updates and timestamps
- Deps: EVE-5

**EVE-8** Text search endpoint and scoring
- P:2  E:3h  L:search,backend
- Status: ✅ COMPLETED
- Desc: Support `$text` search with `$meta: "textScore"` sorting and projection.
- AC:
  - `/api/events?q=...` returns results sorted by relevance
  - Includes `score` in response for debugging
- Deps: EVE-6,EVE-7

**EVE-9** Cursor-based pagination for events list
- P:1  E:3h  L:performance,backend
- Status: ✅ COMPLETED
- Desc: Implement `_id` cursor pagination in service and API responses.
- AC:
  - Response contains `next_cursor`, `has_more`
  - Works with category and search filters
- Deps: EVE-7

**EVE-10** Weekend window calculation util
- P:3  E:2h  L:utils,backend
- Status: ✅ COMPLETED
- Desc: Utility to compute Friday 6pm → Sunday 11:59pm in UTC.
- AC:
  - Covered by unit tests for boundary conditions
- Deps: EVE-7

**EVE-36** Reviews collection implementation
- P:2  E:4h  L:database,schema,backend
- Desc: Add new 'Reviews' collection to store feedback linked to events and venues with proper schema validation and CRUD operations.
- AC:
  - Reviews collection schema defined with required fields (event_id/venue_id, user_id, rating, comment, created_at)
  - JSON Schema validation enforces rating bounds (1-5) and required fields
  - CRUD service methods for creating, reading, updating, and deleting reviews
  - Query methods to fetch reviews by event_id or venue_id with pagination
  - Unit tests cover happy-path and validation scenarios
  - Indexes created for event_id, venue_id, user_id, and created_at
- Deps: EVE-5

**EVE-37** Enhanced check-ins bridge table implementation
- P:2  E:5h  L:database,schema,backend,analytics
- Desc: Implement enhanced check-ins collection as bridge table with analytics capabilities, comprehensive indexing, and attendance tracking features.
- AC:
  - Enhanced check-ins schema with venue_id denormalization, check_in_method, metadata fields
  - JSON Schema validation for all required fields and data constraints
  - CRUD service methods with duplicate prevention (event_id + user_id unique constraint)
  - Analytics query methods for attendance patterns, venue statistics, repeat attendees
  - Comprehensive index suite for all query patterns and performance optimization
  - Unit tests cover bridge table functionality and analytics queries
- Deps: EVE-5

---

## Phase 2 – Geospatial & Discovery

**EVE-11** Nearby events GeoJSON API
- P:1  E:3h  L:geo,api
- Status: ✅ COMPLETED
- Desc: `$geoNear` aggregation with radius and limit returning GeoJSON FeatureCollection.
- AC:
  - `/api/events/nearby` returns valid GeoJSON
  - Distance in meters rounded to 2 decimals
- Deps: EVE-6

**EVE-12** Weekend near-me discovery API
- P:2  E:3h  L:geo,api
- Status: ✅ COMPLETED
- Desc: Combine `$geoNear` with weekend date-range filter.
- AC:
  - `/api/events/weekend` responds within target latency on 10k docs
- Deps: EVE-10,EVE-11

**EVE-13** Category filter + geo + date compound query
- P:2  E:3h  L:geo,search
- Status: ✅ COMPLETED
- Desc: Add optional `category` to geospatial/date queries; verify compound index usage.
- AC:
  - Explain shows index usage without collection scan
- Deps: EVE-6,EVE-11,EVE-12

**EVE-14** Map-ready sample page
- P:3  E:3h  L:frontend,ux
- Status: ✅ COMPLETED
- Desc: Simple page integrating map placeholder and fetch from nearby API.
- AC:
  - Visual markers for events (can be mocked initially)
- Deps: EVE-11

**EVE-38** Event address support with geocoding
- P:3  E:5h  L:geo,backend,api
- Desc: Add optional address field to events with Google Maps geocoding integration for bidirectional coordinate/address conversion and directions links.
- AC:
  - Event schema includes optional `address` field with street, city, state, zip, country structure
  - Google Maps Geocoding API integration for address→coordinates conversion
  - Reverse geocoding for coordinates→address conversion when address missing
  - Google Maps directions URL generated and stored on event creation
  - Robust validation ensures address can be geocoded or coordinates can be reverse-geocoded
  - API endpoints support address-based event creation and updates
  - Error handling for geocoding failures with fallback options
  - Environment configuration for Google Maps API key setup
- Deps: EVE-5,EVE-7

---

## Phase 3 – Analytics & Aggregations

**EVE-15** Peak times aggregation
- P:2  E:3h  L:analytics
- Status: ✅ COMPLETED
- Desc: `$group` by hour and dayOfWeek with counts.
- AC:
  - `/api/analytics` returns top 10 peak buckets
- Deps: EVE-7

**EVE-16** Category popularity aggregation
- P:2  E:2h  L:analytics
- Desc: Counts per category; include average `max_attendees`.
- AC:
  - Sorted by count desc; includes `avg_attendees`
- Deps: EVE-7

**EVE-17** Monthly trends aggregation
- P:3  E:2h  L:analytics
- Desc: Group by year/month and sort ascending.
- AC:
  - `/api/analytics` returns monthly series suitable for charting
- Deps: EVE-7

**EVE-18** Analytics performance budget
- P:3  E:2h  L:performance,analytics
- Desc: Validate analytics latency on 10k docs; document explain stats.
- AC:
  - Each aggregation < 200ms on seeded dataset
  - Notes recorded in `docs/course-report.md`
- Deps: EVE-15,EVE-16,EVE-17

---

## Phase 4 – Real-time & Change Streams

**EVE-19** Socket.IO server plumbing
- P:1  E:3h  L:realtime,backend
- Desc: Initialize SocketIO, events and analytics namespaces.
- AC:
  - Server boots; client can connect and receive a welcome ping
- Deps: EVE-7

**EVE-20** MongoDB change streams listener
- P:1  E:4h  L:realtime,database
- Desc: Watch `events` collection; handle insert/update/delete.
- AC:
  - Broadcasts `event_created`, `event_updated`, `event_deleted`
- Deps: EVE-19

**EVE-21** Location/category rooms
- P:2  E:3h  L:realtime
- Desc: Allow joining rooms keyed by location window or category; prepare for scoped broadcasts.
- AC:
  - Join/leave acknowledge events; room naming stable
- Deps: EVE-20

**EVE-22** Real-time demo page
- P:3  E:3h  L:frontend,realtime
- Desc: `/realtime` page shows feed of new/updated/deleted events and analytics pings.
- AC:
  - Manual test: creating an event triggers client update
- Deps: EVE-19,EVE-20,EVE-21

---

## Phase 5 – Data Generation & Benchmarking

**EVE-23** 10k events generator
- P:1  E:3h  L:data,tooling
- Desc: Generate realistic events across US cities; JSON export.
- AC:
  - `test_events.json` generated; passes JSON validation
- Deps: EVE-5

**EVE-24** Import + seed script docs
- P:2  E:1h  L:docs,tooling
- Desc: Instructions for `mongoimport` and environment.
- AC:
  - README section with exact commands
- Deps: EVE-23

**EVE-25** Performance harness
- P:2  E:4h  L:testing,performance
- Desc: `test_performance.py` measures inserts, queries, aggregations, pagination.
- AC:
  - Console summary and per-test timings; explain snapshots saved to disk
- Deps: EVE-23

**EVE-26** Baseline performance report
- P:2  E:3h  L:docs,performance
- Desc: Capture baseline metrics and include in `docs/course-report.md`.
- AC:
  - Table of p50/p95 latencies per workload
- Deps: EVE-25

---

## Phase 6 – Transactions & Consistency

**EVE-27** Booking flow design
- P:2  E:3h  L:design,transactions
- Desc: Specify multi-document transaction steps for ticket booking.
- AC:
  - Sequence diagram + pseudo code; failure modes listed
- Deps: EVE-5,EVE-7

**EVE-28** Booking API (transactional)
- P:2  E:6h  L:backend,transactions
- Desc: Implement transaction: check capacity → decrement → create check-in.
- AC:
  - Rollback on error; idempotent retry strategy noted
- Deps: EVE-27

**EVE-29** Contention tests on seat inventory
- P:3  E:4h  L:testing,performance
- Desc: Simulate concurrent bookings; measure conflicts and throughput.
- AC:
  - Results table and discussion in course report
- Deps: EVE-28

---

## Phase 7 – Quality, Security, DX

**EVE-30** Input validation & error handling audit
- P:2  E:3h  L:quality,security
- Desc: Consistent error messages; Pydantic validations enforced on all APIs.
- AC:
  - 4xx vs 5xx semantics correct; helpful error payloads
- Deps: EVE-7

**EVE-31** Linting and formatting CI (local/script)
- P:3  E:2h  L:devx
- Desc: Ensure ruff/black run clean; pre-commit or script documented.
- AC:
  - Zero warnings; command documented in README

**EVE-32** Configuration hardening
- P:3  E:2h  L:security,ops
- Desc: `.env` handling, required vars, non-default secrets for production profile.
- AC:
  - App fails fast when critical env vars missing in prod mode

**EVE-33** API documentation snapshot
- P:3  E:2h  L:docs,api
- Desc: Document available endpoints, params, sample responses.
- AC:
  - `docs/api.md` created with examples and curl snippets

**EVE-34** Final write-up and presentation assets
- P:2  E:4h  L:docs
- Desc: Summarize outcomes: benchmarks, design decisions, trade-offs; slides or outline.
- AC:
  - `docs/course-report.md` updated; final metrics and reflections included
- Deps: EVE-26,EVE-29,EVE-30–EVE-33

**EVE-35** Timezone modernization and datetime.utcnow() deprecation
- P:2  E:3h  L:quality,security,backend,refactoring
- Desc: Systematically replace all instances of deprecated `datetime.utcnow()` with timezone-aware `datetime.now(timezone.utc)` throughout the codebase.
- AC:
  - All `datetime.utcnow()` calls replaced with `datetime.now(timezone.utc)`
  - All files import `timezone` from datetime module where needed
  - All tests pass without deprecation warnings
  - No functionality changes - only timezone awareness improvements
- Deps: None

**EVE-36** Reviews collection implementation
- P:1  E:4h  L:database,schema,backend
- Status: ✅ COMPLETED
- Desc: Add new 'Reviews' collection to store feedback linked to events and venues with proper schema validation and CRUD operations.
- AC:
  - Reviews collection schema defined with required fields (event_id/venue_id, user_id, rating, comment, created_at)
  - JSON Schema validation enforces rating bounds (1-5) and required fields
  - CRUD service methods for creating, reading, updating, and deleting reviews
  - Query methods to fetch reviews by event_id or venue_id with pagination
  - Unit tests cover happy-path and validation scenarios
  - Indexes created for event_id, venue_id, user_id, and created_at
- Deps: EVE-5

**EVE-37** Enhanced check-ins bridge table implementation
- P:1  E:5h  L:database,schema,analytics,backend
- Desc: Implement enhanced check-ins collection as bridge table with analytics capabilities, comprehensive indexing, and attendance tracking features.
- AC:
  - Enhanced check-ins schema with venue_id denormalization, check_in_method, metadata fields
  - JSON Schema validation for all required fields and data constraints
  - CRUD service methods with duplicate prevention (event_id + user_id unique constraint)
  - Analytics query methods for attendance patterns, venue statistics, repeat attendees
  - Comprehensive index suite for all query patterns and performance optimization
  - Unit tests cover bridge table functionality and analytics queries
- Deps: EVE-5

---

## Backlog Labels
- database, schema, indexing, performance, backend, api, geo, analytics, realtime, transactions, testing, docs, security, devx, tooling, frontend, quality, refactoring

## Notes
- This plan assumes a single-developer cadence over ~6–8 weeks. Adjust estimates as data emerges.
- Use this as a Linear backlog import (titles map 1:1). Additional subtasks can be added under each ticket as implementation details evolve.
