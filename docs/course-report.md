# CSCI 485 – MongoDB Course Report (Living Document)

This living document ties the project's architecture and implementation work directly to CSCI 485 outcomes. It will be updated as features are added, experiments are run, and results are collected.

## 1) Project Overview and Learning Goals

- **Domain**: Event Discovery and Check-In System with Geospatial Analytics
- **Primary DB**: MongoDB (document model, GeoJSON, aggregations, change streams)
- **Course Learning Alignment**:
  - Modeling non-relational data for real applications (events, venues, check-ins)
  - Index design and query planning for performance at scale
  - Advanced MongoDB features: text search, geospatial, aggregations, transactions
  - Real-time data processing using change streams and WebSockets
  - Benchmarking, explain plans, and optimization

## 2) Data Model and Justification (Course Concepts)

- **Document Model Rationale**: Events have heterogeneous attributes; embedding provides efficient reads; references used for shared entities (venues, users). Demonstrates schema flexibility vs. rigid relational schemas.
- **Collections**: `events`, `venues`, `users`, `checkins`, `reviews`, `tickets`
- **Embedding vs Referencing**:
  - Embed: `tickets[]`, `attendees[]` (frequent co-access, small bounded growth)
  - Reference: `venue_id`, `user_id`, `event_id` (shared, potentially large fan-out)
- **Validation**: JSON Schema rules (required fields, GeoJSON structure, numeric bounds) to show controlled flexibility.
- **Identifiers**: `ObjectId` for distributed, timestamped IDs; enables cursor pagination and time-aware operations.

References: See `DATABASE_DESIGN.md` (Schema, Relationships, Validation)

## 3) Query Workloads and Index Strategy (Planned and Implemented)

- **Discovery**:
  - Text search across `title`, `description`, `tags` using MongoDB text index
  - Category filtering + chronological sorting
  - Geospatial discovery via `$geoNear` on `location` (2dsphere)
- **Temporal**:
  - Upcoming events, weekend windows, date ranges
- **Analytics**:
  - Peak hours/days, category popularity, monthly trends (aggregation pipeline)
- **Pagination**:
  - Cursor-based pagination using `_id` to avoid `skip` penalties

- **Indexes Implemented** (examples):
  - `location: "2dsphere"`
  - Text index on `title, description, category, tags`
  - `start_date`, `created_at`
  - Compound: `(category, start_date)`, `(location:2dsphere, start_date)`, `(organizer, start_date)`

References: `app/database.py`, `app/services.py`

## 4) Advanced MongoDB Features (Course Outcomes)

- **Geospatial**: `$geoNear`, GeoJSON, 2dsphere index – supports "events near me this weekend" use case.
- **Text Search**: Multi-field index with relevance; explore `$meta: "textScore"` ordering.
- **Aggregations**: `$group`, `$sort`, time extraction operators for analytics.
- **Change Streams**: Real-time updates on `events` collection broadcast via WebSockets.
- **Transactions** (design-ready): Multi-document workflow for ticket booking (seat decrement + check-in creation) to illustrate ACID in MongoDB.

References: `app/realtime.py`, `app/services.py`

## 5) Performance Methodology (Experiments You’ll Run)

- **Datasets**:
  - Synthetic: `generate_test_data.py` (10,000+ events across 1,000+ geo points)
- **Benchmarks**: `test_performance.py`
  - Insert throughput (docs/sec)
  - Text search latency (p50/p95)
  - Geospatial query latency vs. radius and density
  - Date-range and compound filter latency
  - Aggregation latency (peak/weekly trends)
  - Pagination: cursor vs. offset
- **Explain Plans**:
  - Capture `explain()` for representative queries; record `keys examined`, `docs examined`, `executionTimeMillis`.
- **Success Criteria (targets, adjustable)**:
  - Geospatial < 50 ms, Text Search < 100 ms, Aggregations < 200 ms on 10k docs

Artifacts: tables/plots of latency, index usage notes, bottlenecks and fixes.

## 6) CAP & Consistency Trade-offs (Analytical Write-up)

- **Priority**: Availability + Partition Tolerance for discovery; strong consistency for ticket booking.
- **Eventual Consistency** acceptable for: attendee counts, analytics, recommendations.
- **Strong Consistency** required for: seat inventory, payments (transactional section).
- **Discussion**: Reflect on BASE vs ACID in different subsystems.

## 7) Real-Time Component (Course Topic: Streams)

- **Design**: MongoDB Change Streams → Flask-SocketIO → browser clients
- **Use cases**: New events, updates, deletions; optional room subscriptions (by location/category)
- **Evaluation**: Measure end-to-end latency from write → socket broadcast → client receipt.

References: `app/realtime.py`, `app/templates/realtime_demo.html`

## 8) Security, Ethics, and Data Quality

- **Security**: Principle of least privilege in MongoDB roles; environment variables for credentials.
- **Privacy**: Avoid storing unnecessary PII; anonymize analytics; discuss GDPR-style concerns.
- **Data Quality**: Schema validation; coordinate bounds checks; date integrity (end after start).

## 9) Scaling and Polyglot Strategy

- **Sharding**: Potential shard keys – `location` (geo buckets), `start_date` (time windows), or hashed `_id`.
- **Caching**: Redis for hot queries (popular areas, near-term dates).
- **Polyglot**: MongoDB (events), SQL (payments/auth), Redis (sessions), Elastic (advanced search) – articulate trade-offs.

## 10) Semester Plan & Milestones (Update as You Go)

- Week 1–2: Finalize schema/indexes; seed 10k dataset; baseline benchmarks
- Week 3–4: Implement analytics dashboards; capture explain plans; tune indexes
- Week 5–6: Real-time pipeline; measure update latency; optional room filters
- Week 7–8: Transactions for booking; contention tests on seat inventory
- Week 9–10: Scaling experiments (index size, memory, cache efficacy)
- Week 11–12: Write-up: performance results, lessons learned, trade-offs
- Week 13–14: Polish and present; optional sharding exploration

Deliverables each milestone: code edits, metrics, explain snapshots, reflection notes.

## 11) How to Reproduce (Evaluator/TA Checklist)

- Generate data: `python generate_test_data.py`
- Import data: `python generate_test_data.py --seed-db --clear-db` (or use mongoimport commands)
- Run app: `python -m app` → visit `/realtime` and `/api/*`
- Run benchmarks: `python test_performance.py`
- Inspect design: `DATABASE_DESIGN.md` and this report

## 12) Reflection Prompts (Fill During Semester)

- What index changes had the biggest effect and why?
- Where did index intersection or wrong index choice hurt performance?
- How did cursor pagination affect user-perceived latency vs. offset?
- What trade-offs did you make between embedding and referencing?
- Where is strong consistency required, and how was it achieved?
- How would you shard this in production and what are risks?