# Linear Backlog – Mongo Events Demo (30 tickets)

This is a living backlog to drive end-to-end delivery. Tickets are grouped by phases and include acceptance criteria (AC), estimates, and dependencies (Deps).

Legend: P = priority (1 highest), E = estimate (ideal hours), L = labels

---

## Phase 1 – Foundations (Schema, Indexes, CRUD)

1) Schema finalization and validation
- P:1  E:4h  L:database,schema
- Desc: Finalize `events`, `venues`, `users`, `checkins` schemas with JSON Schema validation.
- AC:
  - Events collection enforces required fields and GeoJSON structure
  - Coordinate bounds validated
  - `DATABASE_DESIGN.md` matches implemented schema

2) Index suite implementation in app/database.py
- P:1  E:3h  L:indexing,performance
- Desc: Ensure all indexes exist: 2dsphere, text, start_date, category+start_date, location+start_date, organizer+start_date, created_at, tags.
- AC:
  - `list_indexes` shows all specified indexes
  - Index build idempotent at startup
- Deps: 1

3) CRUD services parity and unit tests
- P:1  E:4h  L:backend,testing
- Desc: Verify create/get/update/delete paths and add unit tests.
- AC:
  - Tests cover happy-path and invalid ObjectId
  - Update respects partial updates and timestamps
- Deps: 1

4) Text search endpoint and scoring
- P:2  E:3h  L:search,backend
- Desc: Support `$text` search with `$meta: "textScore"` sorting and projection.
- AC:
  - `/api/events?q=...` returns results sorted by relevance
  - Includes `score` in response for debugging
- Deps: 2,3

5) Cursor-based pagination for events list
- P:1  E:3h  L:performance,backend
- Desc: Implement `_id` cursor pagination in service and API responses.
- AC:
  - Response contains `next_cursor`, `has_more`
  - Works with category and search filters
- Deps: 3

6) Weekend window calculation util
- P:3  E:2h  L:utils,backend
- Desc: Utility to compute Friday 6pm → Sunday 11:59pm in UTC.
- AC:
  - Covered by unit tests for boundary conditions
- Deps: 3

---

## Phase 2 – Geospatial & Discovery

7) Nearby events GeoJSON API
- P:1  E:3h  L:geo,api
- Desc: `$geoNear` aggregation with radius and limit returning GeoJSON FeatureCollection.
- AC:
  - `/api/events/nearby` returns valid GeoJSON
  - Distance in meters rounded to 2 decimals
- Deps: 2

8) Weekend near-me discovery API
- P:2  E:3h  L:geo,api
- Desc: Combine `$geoNear` with weekend date-range filter.
- AC:
  - `/api/events/weekend` responds within target latency on 10k docs
- Deps: 6,7

9) Category filter + geo + date compound query
- P:2  E:3h  L:geo,search
- Desc: Add optional `category` to geospatial/date queries; verify compound index usage.
- AC:
  - Explain shows index usage without collection scan
- Deps: 2,7,8

10) Map-ready sample page
- P:3  E:3h  L:frontend,ux
- Desc: Simple page integrating map placeholder and fetch from nearby API.
- AC:
  - Visual markers for events (can be mocked initially)
- Deps: 7

---

## Phase 3 – Analytics & Aggregations

11) Peak times aggregation
- P:2  E:3h  L:analytics
- Desc: `$group` by hour and dayOfWeek with counts.
- AC:
  - `/api/analytics` returns top 10 peak buckets
- Deps: 3

12) Category popularity aggregation
- P:2  E:2h  L:analytics
- Desc: Counts per category; include average `max_attendees`.
- AC:
  - Sorted by count desc; includes `avg_attendees`
- Deps: 3

13) Monthly trends aggregation
- P:3  E:2h  L:analytics
- Desc: Group by year/month and sort ascending.
- AC:
  - `/api/analytics` returns monthly series suitable for charting
- Deps: 3

14) Analytics performance budget
- P:3  E:2h  L:performance,analytics
- Desc: Validate analytics latency on 10k docs; document explain stats.
- AC:
  - Each aggregation < 200ms on seeded dataset
  - Notes recorded in `docs/course-report.md`
- Deps: 11,12,13

---

## Phase 4 – Real-time & Change Streams

15) Socket.IO server plumbing
- P:1  E:3h  L:realtime,backend
- Desc: Initialize SocketIO, events and analytics namespaces.
- AC:
  - Server boots; client can connect and receive a welcome ping
- Deps: 3

16) MongoDB change streams listener
- P:1  E:4h  L:realtime,database
- Desc: Watch `events` collection; handle insert/update/delete.
- AC:
  - Broadcasts `event_created`, `event_updated`, `event_deleted`
- Deps: 15

17) Location/category rooms
- P:2  E:3h  L:realtime
- Desc: Allow joining rooms keyed by location window or category; prepare for scoped broadcasts.
- AC:
  - Join/leave acknowledge events; room naming stable
- Deps: 16

18) Real-time demo page
- P:3  E:3h  L:frontend,realtime
- Desc: `/realtime` page shows feed of new/updated/deleted events and analytics pings.
- AC:
  - Manual test: creating an event triggers client update
- Deps: 15,16,17

---

## Phase 5 – Data Generation & Benchmarking

19) 10k events generator
- P:1  E:3h  L:data,tooling
- Desc: Generate realistic events across US cities; JSON export.
- AC:
  - `test_events.json` generated; passes JSON validation
- Deps: 1

20) Import + seed script docs
- P:2  E:1h  L:docs,tooling
- Desc: Instructions for `mongoimport` and environment.
- AC:
  - README section with exact commands
- Deps: 19

21) Performance harness
- P:2  E:4h  L:testing,performance
- Desc: `test_performance.py` measures inserts, queries, aggregations, pagination.
- AC:
  - Console summary and per-test timings; explain snapshots saved to disk
- Deps: 19

22) Baseline performance report
- P:2  E:3h  L:docs,performance
- Desc: Capture baseline metrics and include in `docs/course-report.md`.
- AC:
  - Table of p50/p95 latencies per workload
- Deps: 21

---

## Phase 6 – Transactions & Consistency

23) Booking flow design
- P:2  E:3h  L:design,transactions
- Desc: Specify multi-document transaction steps for ticket booking.
- AC:
  - Sequence diagram + pseudo code; failure modes listed
- Deps: 1,3

24) Booking API (transactional)
- P:2  E:6h  L:backend,transactions
- Desc: Implement transaction: check capacity → decrement → create check-in.
- AC:
  - Rollback on error; idempotent retry strategy noted
- Deps: 23

25) Contention tests on seat inventory
- P:3  E:4h  L:testing,performance
- Desc: Simulate concurrent bookings; measure conflicts and throughput.
- AC:
  - Results table and discussion in course report
- Deps: 24

---

## Phase 7 – Quality, Security, DX

26) Input validation & error handling audit
- P:2  E:3h  L:quality,security
- Desc: Consistent error messages; Pydantic validations enforced on all APIs.
- AC:
  - 4xx vs 5xx semantics correct; helpful error payloads
- Deps: 3

27) Linting and formatting CI (local/script)
- P:3  E:2h  L:devx
- Desc: Ensure ruff/black run clean; pre-commit or script documented.
- AC:
  - Zero warnings; command documented in README

28) Configuration hardening
- P:3  E:2h  L:security,ops
- Desc: `.env` handling, required vars, non-default secrets for production profile.
- AC:
  - App fails fast when critical env vars missing in prod mode

29) API documentation snapshot
- P:3  E:2h  L:docs,api
- Desc: Document available endpoints, params, sample responses.
- AC:
  - `docs/api.md` created with examples and curl snippets

30) Final write-up and presentation assets
- P:2  E:4h  L:docs
- Desc: Summarize outcomes: benchmarks, design decisions, trade-offs; slides or outline.
- AC:
  - `docs/course-report.md` updated; final metrics and reflections included
- Deps: 22,25,26–29

---

## Backlog Labels
- database, schema, indexing, performance, backend, api, geo, analytics, realtime, transactions, testing, docs, security, devx, tooling, frontend

## Notes
- This plan assumes a single-developer cadence over ~6–8 weeks. Adjust estimates as data emerges.
- Use this as a Linear backlog import (titles map 1:1). Additional subtasks can be added under each ticket as implementation details evolve.
