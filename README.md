# MongoDB Events Demo

A full-stack web application demonstrating MongoDB's geospatial capabilities with event management and mapping features. This project showcases the integration of modern web technologies with NoSQL database geospatial features to create an interactive event discovery platform.

## Project Overview

This application serves as a comprehensive demonstration of how to build location-aware web applications using MongoDB's geospatial capabilities. The system allows users to discover, create, and manage events through an interactive map interface, leveraging advanced database queries for location-based search and filtering.

## Key Features

### Interactive Event Map
- **Leaflet.js Integration**: Interactive maps with OpenStreetMap tiles for seamless geographic visualization
- **Real-time Search**: Dynamic event discovery with radius-based filtering
- **Location Selection**: Click-to-select functionality for creating new events at specific coordinates
- **Current Location Detection**: Automatic geolocation for user convenience
- **Interactive Markers**: Pop-up details and event information on map markers

### Event Management System
- **Complete CRUD Operations**: Create, view, edit, and delete events with full validation
- **Location-based Search**: Find events within specified geographic areas
- **Category Organization**: Structured event categorization for better discovery
- **Date Management**: Start and end date validation with timezone support

### RESTful API Architecture
- **RESTful Design**: Clean, predictable API endpoints following REST principles
- **GeoJSON Support**: Standardized geographic data format for map integration
- **Pagination**: Efficient data loading with pagination support
- **Query Parameters**: Flexible filtering and search capabilities

### Data Validation & Security
- **Pydantic Models**: Robust data validation ensuring data integrity
- **Coordinate Validation**: Geographic coordinate range validation
- **Date Validation**: Temporal logic validation (end dates after start dates)
- **Type Safety**: Comprehensive type checking throughout the application

## Technical Architecture

### Backend Technologies
- **Python 3.11**: Modern Python with latest language features
- **Flask**: Lightweight web framework with Jinja2 templating
- **PyMongo**: Official MongoDB driver for Python with geospatial support
- **Pydantic**: Data validation and serialization with automatic type conversion
- **python-dotenv**: Environment configuration management

### Frontend Technologies
- **Jinja2 Templates**: Server-side rendering with dynamic content
- **Bootstrap 5**: Responsive CSS framework for modern UI components
- **Alpine.js**: Lightweight JavaScript framework for interactive components
- **Leaflet.js**: Open-source mapping library with extensive plugin ecosystem

### Database Design
- **MongoDB**: Document-based NoSQL database with geospatial capabilities
- **2dsphere Indexes**: Optimized geospatial indexing for location queries
- **GeoJSON Format**: Standardized geographic data representation
- **Aggregation Pipeline**: Complex geospatial queries using MongoDB aggregation

## Geospatial Implementation

### Database Queries
The application leverages MongoDB's advanced geospatial features:

- **$geoNear Aggregation**: Distance-based event search with customizable radius
- **2dsphere Indexes**: High-performance geospatial indexing for location queries
- **GeoJSON Integration**: Seamless map data format compatibility
- **Spatial Filtering**: Complex geographic boundary and proximity queries

### Map Integration
- **OpenStreetMap Tiles**: Free, open-source mapping data
- **Interactive Controls**: Zoom, pan, and location selection functionality
- **Marker Clustering**: Efficient display of multiple nearby events
- **Responsive Design**: Mobile-friendly map interface

## Project Structure

```
mongo-events-demo/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── models.py            # Pydantic data models
│   ├── database.py          # MongoDB connection management
│   ├── services.py          # Business logic layer
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # Static files (CSS, JS)
├── data/
│   └── generate_sample_data.py  # Faker data generation
├── tests/
│   ├── __init__.py
│   └── test_app.py          # Application tests
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Tool configuration
└── run.py                   # Application entry point
```

## API Design

### Event Management Endpoints
- `GET /api/events` - List events with pagination and filtering
- `POST /api/events` - Create new event with validation
- `GET /api/events/<id>` - Retrieve specific event details
- `PUT /api/events/<id>` - Update existing event
- `DELETE /api/events/<id>` - Remove event from system

### Geospatial Endpoints
- `GET /api/events/nearby` - Find events within specified radius
  - Query parameters: `lat`, `lng`, `radius` (km), `limit`
  - Returns GeoJSON formatted results for map integration

### Utility Endpoints
- `GET /api/categories` - Retrieve available event categories

## Frontend Interface

### User Interface Routes
- `/` - Interactive map view with event discovery
- `/events` - Comprehensive events list with filtering options
- `/events/new` - Event creation form with map integration
- `/events/<id>` - Detailed event information page

### User Experience Features
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Real-time Updates**: Dynamic content updates without page refresh
- **Intuitive Navigation**: Clear user flow for event discovery and management
- **Accessibility**: Semantic HTML and keyboard navigation support

## Development Practices

### Code Quality
- **Type Safety**: Comprehensive type hints and Pydantic validation
- **Code Formatting**: Automated code formatting with Black
- **Linting**: Static analysis with Ruff for code quality
- **Testing**: Comprehensive test suite with pytest

### Data Management
- **Sample Data Generation**: Faker-based realistic test data creation
- **Database Seeding**: Automated sample data population for development
- **Environment Configuration**: Secure configuration management

## Technical Achievements

### Geospatial Innovation
- **Advanced Queries**: Complex MongoDB geospatial aggregation pipelines
- **Performance Optimization**: Efficient indexing strategies for location-based searches
- **Map Integration**: Seamless integration between database and mapping interface

### Full-Stack Integration
- **API-First Design**: Clean separation between frontend and backend
- **Data Validation**: End-to-end data integrity with Pydantic models
- **Responsive UI**: Modern, mobile-friendly user interface

### Scalability Considerations
- **Database Optimization**: Efficient query patterns and indexing strategies
- **Caching Strategy**: Optimized data retrieval for map interactions
- **Modular Architecture**: Clean separation of concerns for maintainability

## Data Generation & Seeding

### Comprehensive Test Data Generator

The project includes a sophisticated test data generator (`generate_test_data.py`) that creates realistic sample data for development and testing.

#### Features
- **10,000+ Events**: Realistic events across major US cities with proper geospatial coordinates
- **500+ Venues**: Diverse venues with capacity, amenities, and contact information
- **2,000+ Users**: User profiles with preferences and location data
- **5,000+ Tickets**: Ticket sales with realistic pricing and availability
- **Reviews & Check-ins**: User feedback and attendance tracking
- **JSON Export**: Export data for external use or backup
- **Direct Database Seeding**: Populate MongoDB directly with generated data

#### Usage Options

**1. Generate JSON Files Only (Default)**
```bash
python generate_test_data.py --json-only
```
This creates:
- `test_events.json` - 10,000 events with geospatial data
- `test_venues.json` - 500 venues with location and capacity info
- `test_users.json` - 2,000 user profiles
- `test_tickets.json` - 5,000 ticket records
- `test_checkins.json` - Check-in records for analytics
- `test_reviews.json` - User reviews and ratings

**2. Direct Database Seeding**
```bash
python generate_test_data.py --seed-db --clear-db
```
This will:
- Clear existing data (optional with `--clear-db`)
- Generate comprehensive test data
- Insert directly into MongoDB
- Provide seeding progress and statistics

**3. Custom Data Volumes**
```bash
python generate_test_data.py --seed-db --events 5000 --venues 250 --users 1000
```

#### MongoDB Import Commands

If you prefer to use `mongoimport` with the generated JSON files:

```bash
# Import events (ensure 2dsphere index exists first)
mongoimport --db events_db --collection events --file test_events.json --jsonArray

# Import venues
mongoimport --db events_db --collection venues --file test_venues.json --jsonArray

# Import users
mongoimport --db events_db --collection users --file test_users.json --jsonArray

# Import tickets
mongoimport --db events_db --collection tickets --file test_tickets.json --jsonArray

# Import checkins
mongoimport --db events_db --collection checkins --file test_checkins.json --jsonArray

# Import reviews
mongoimport --db events_db --collection reviews --file test_reviews.json --jsonArray
```

#### Environment Setup

Ensure your MongoDB connection is configured in `eventdb/config.py`:

```python
MONGODB_URI = "mongodb://localhost:27017"
DB_NAME = "events_db"
```

#### Data Characteristics

**Geographic Distribution**
- Events distributed across 50+ major US cities
- Realistic coordinate variations within city boundaries
- Proper GeoJSON Point format for MongoDB 2dsphere indexes

**Temporal Distribution**
- Events spanning 3 months (1 month past, 2 months future)
- Realistic time distributions (more events on weekends)
- Proper timezone handling with UTC timestamps

**Category Distribution**
- 16 diverse event categories
- Realistic category-to-title mappings
- Balanced distribution across categories

**User Engagement**
- Realistic review patterns (40% of events have reviews)
- Check-in data for analytics and attendance tracking
- User preferences and location data

#### Performance Testing

The generated data is optimized for performance testing:
- Large enough dataset (10k+ events) for meaningful benchmarks
- Realistic geospatial distribution for proximity queries
- Proper indexing requirements for optimal query performance
- Analytics-ready data for aggregation testing

## Future Enhancements

- User authentication and event ownership management
- Advanced event categorization with custom icons
- Enhanced filtering capabilities (date ranges, attendee limits)
- Event registration and RSVP system
- Email notifications and event reminders
- Social media integration and sharing
- Progressive Web App (PWA) support for mobile users

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.