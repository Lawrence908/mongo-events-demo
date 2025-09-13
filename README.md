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