# MongoDB Events Demo - Project Structure

## 🏗️ Current Organization

```
mongo-events-demo/
├── app/                          # Main Flask application
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Application configuration
│   ├── models.py                # Pydantic models (updated with polymorphic patterns)
│   ├── services.py              # Business logic services
│   ├── database.py              # Database connection management
│   ├── schema_validation.py     # MongoDB schema validation
│   ├── realtime.py              # WebSocket/real-time features
│   ├── geocoding.py             # Google Maps integration
│   ├── utils.py                 # Utility functions
│   ├── static/                  # CSS, JS, images
│   └── templates/               # HTML templates
├── docs/                        # Documentation
│   └── viu/
│       └── deliverables/2/      # Assignment deliverables
│           ├── 2.database-design-architecture.md
│           ├── create_collections.js
│           ├── create_indexes.js
│           └── sample_data.js
├── generate_test_data.py        # Test data generator
├── run.py                       # Application entry point
├── DATABASE_DESIGN.md           # Comprehensive database design
└── README.md                    # Project overview
```

## 🎯 Key Features Implemented

### ✅ Advanced Design Patterns
- **Polymorphism**: Events and venues with type-specific attributes
- **Schema Versioning**: All collections include `schemaVersion` field
- **Computed Pattern**: Pre-calculated statistics for performance
- **Extended Reference**: Venue data embedded in events for fast queries

### ✅ Database Collections
- `events` - Polymorphic event catalog with geospatial support
- `venues` - Polymorphic venue catalog with type-specific details
- `users` - User profiles with preferences
- `checkins` - Bridge collection for attendance analytics
- `reviews` - Event and venue reviews

### ✅ Application Features
- **Geospatial Queries**: Find events near location
- **Text Search**: Full-text search across events
- **Real-time Updates**: WebSocket integration
- **Analytics**: Attendance and review analytics
- **REST API**: Complete CRUD operations

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Database
```bash
# Create collections with validation
mongosh < docs/viu/deliverables/2/create_collections.js

# Create indexes
mongosh < docs/viu/deliverables/2/create_indexes.js

# Insert sample data
mongosh < docs/viu/deliverables/2/sample_data.js
```

### 3. Generate Test Data
```bash
# Generate and seed database
python generate_test_data.py --seed-db --clear-db --events 1000 --venues 100 --users 500
```

### 4. Run Application
```bash
python run.py
```

## 📊 Database Design Highlights

### Polymorphic Event Types
- `in_person` - Traditional physical events
- `virtual` - Online events with meeting details
- `hybrid` - Mixed virtual/in-person events
- `recurring` - Repeat events with scheduling

### Polymorphic Venue Types
- `conference_center` - Meeting rooms, A/V equipment
- `park` - Outdoor spaces, activities
- `restaurant` - Dining venues
- `virtual_space` - Online platforms
- `stadium` - Large venues
- `theater` - Performance venues

### Performance Optimizations
- **Geospatial Indexes**: 2dsphere for location queries
- **Text Search**: Multi-field text indexes
- **Compound Indexes**: Optimized for common query patterns
- **Computed Fields**: Pre-calculated statistics
- **Extended References**: Denormalized data for fast queries

## 🔧 Configuration

Environment variables:
- `MONGODB_URI` - Database connection string
- `MONGODB_DB_NAME` - Database name
- `GOOGLE_MAPS_API_KEY` - For geocoding
- `MAX_EVENTS_LIMIT` - Query limit (default: 100000)

## 📈 Query Examples

### Polymorphic Queries
```javascript
// Find virtual events
db.events.find({ event_type: "virtual" })

// Find conference centers
db.venues.find({ venue_type: "conference_center" })
```

### Extended Reference Queries
```javascript
// Find events at conference centers (no join needed)
db.events.find({ "venue_reference.venue_type": "conference_center" })

// Find events in specific city
db.events.find({ "venue_reference.city": "San Francisco" })
```

### Geospatial Queries
```javascript
// Find events within 10km of location
db.events.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [-122.4194, 37.7749] },
      $maxDistance: 10000
    }
  }
})
```

## 🎓 Academic Deliverables

- **Database Design Document**: `DATABASE_DESIGN.md`
- **Assignment Deliverable**: `docs/viu/deliverables/2/2.database-design-architecture.md`
- **Schema Validation**: `docs/viu/deliverables/2/create_collections.js`
- **Index Strategy**: `docs/viu/deliverables/2/create_indexes.js`
- **Sample Data**: `docs/viu/deliverables/2/sample_data.js`

## 🧹 Cleanup

To remove unused files and folders:
```bash
python cleanup_project.py
```

This will remove:
- Unused `eventdb/` folder
- Generated test JSON files
- Utility scripts
- Other temporary files
