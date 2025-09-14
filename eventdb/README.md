# MongoDB Events Demo

A comprehensive demonstration of MongoDB features including CRUD operations, text search, geospatial queries, aggregations, performance analysis, and transactions. Built with Flask, PyMongo, and modern frontend technologies.

## Features

- **Database Switching**: Toggle between local MongoDB and Cloud Atlas
- **CRUD Lab**: Complete Create, Read, Update, Delete operations
- **Text Search**: Full-text search with relevance scoring
- **Geospatial Queries**: Location-based event discovery with interactive maps
- **Analytics**: Aggregation pipelines for business insights
- **Performance Analysis**: Query explanation and index optimization
- **Transactions**: Atomic ticket purchasing with rollback support
- **Interactive UI**: Bootstrap 5 with Alpine.js for modern user experience

## Tech Stack

### Backend
- **Python 3.11** - Core language
- **Flask** - Web framework with Jinja2 templates
- **PyMongo** - MongoDB driver for database operations
- **Pydantic** - Data validation and serialization
- **python-dotenv** - Environment variable management

### Frontend
- **Jinja2** - Server-side templating
- **Bootstrap 5** - CSS framework (CDN)
- **Alpine.js** - Lightweight JavaScript framework
- **Leaflet.js** - Interactive maps with OpenStreetMap tiles

### Development Tools
- **ruff** - Fast Python linter
- **black** - Code formatter
- **pytest** - Testing framework
- **Faker** - Sample data generation

## Project Structure

```
eventdb/
├── app.py                 # Flask application factory
├── config.py              # Configuration with database switching
├── models.py              # Pydantic data models
├── requirements.txt       # Python dependencies
├── run.py                 # Application entry point
├── db/                    # Database scripts
│   ├── seed.py           # Generate sample data
│   ├── ensure_indexes.py # Create database indexes
│   └── transactions_demo.py # Transaction examples
├── routes/               # API route blueprints
│   ├── events.py         # Event CRUD and search
│   ├── venues.py         # Venue management
│   ├── users.py          # User management
│   ├── analytics.py      # Analytics and aggregations
│   └── admin.py          # Admin and performance tools
├── templates/            # Jinja2 HTML templates
│   └── index.html        # Main application interface
├── static/               # Static assets
│   ├── css/custom.css    # Custom styles
│   └── js/app.js         # Frontend JavaScript
└── playgrounds/          # VS Code MongoDB playground files
    ├── 01_crud.mongodb
    ├── 02_text_search.mongodb
    ├── 03_geo.mongodb
    ├── 04_aggs.mongodb
    └── 05_transactions.mongodb
```

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Database

Create a `.env` file in the project root:

```bash
# Database Configuration
DB_TYPE=local  # or "cloud" for MongoDB Atlas

# Local MongoDB (school network via SSH)
LOCAL_MONGODB_URI=mongodb://localhost:27017/
LOCAL_DB_NAME=eventdb

# Cloud MongoDB Atlas
CLOUD_MONGODB_URI= {mongo_db_URI}
CLOUD_DB_NAME=eventdb

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
HOST=127.0.0.1
PORT=5000
```

### 3. Initialize Database

```bash
# Generate sample data
python db/seed.py

# Create indexes
python db/ensure_indexes.py
```

### 4. Run Application

```bash
python run.py
```

Visit `http://127.0.0.1:5000` to see the application.

## Database Switching

The application supports switching between local and cloud databases:

1. **Local MongoDB**: Set `DB_TYPE=local` in `.env`
2. **Cloud Atlas**: Set `DB_TYPE=cloud` in `.env`
3. **Runtime Switch**: Use the database toggle in the web interface

## API Endpoints

### Events
- `GET /events/` - List events with pagination
- `POST /events/` - Create new event
- `GET /events/<id>` - Get single event
- `PATCH /events/<id>` - Update event
- `DELETE /events/<id>` - Delete event
- `GET /events/search?q=...` - Text search events
- `GET /api/events/nearby?lng=...&lat=...&km=...` - Find nearby events (GeoJSON)

### Venues
- `GET /venues/` - List venues
- `POST /venues/` - Create venue
- `GET /venues/<id>` - Get venue
- `PATCH /venues/<id>` - Update venue
- `DELETE /venues/<id>` - Delete venue

### Users
- `GET /users/` - List users
- `POST /users/` - Create user
- `GET /users/<id>` - Get user
- `PATCH /users/<id>` - Update user
- `DELETE /users/<id>` - Delete user

### Analytics
- `GET /analytics/top-venues?limit=5` - Top venues by event count
- `GET /analytics/sales-by-month` - Monthly sales data
- `GET /analytics/event-stats` - General statistics

### Admin
- `POST /admin/explain` - Explain query execution
- `GET /admin/indexes` - List database indexes
- `GET /admin/stats` - Database statistics

## MongoDB Playgrounds

The `playgrounds/` directory contains VS Code MongoDB playground files demonstrating:

1. **CRUD Operations** - Basic database operations
2. **Text Search** - Full-text search capabilities
3. **Geospatial Queries** - Location-based queries
4. **Aggregations** - Complex data analysis
5. **Transactions** - Atomic operations and consistency

## Key Features

### Geospatial Queries
- **2dsphere indexes** for location-based queries
- **$geoNear aggregation** for distance-based search
- **GeoJSON format** for map integration
- **Interactive Leaflet maps** with real-time updates

### Text Search
- **Multi-field text indexes** on title, description, and tags
- **Relevance scoring** with `$meta: "textScore"`
- **Phrase search** and exclusion support
- **Language-specific** search capabilities

### Analytics
- **Aggregation pipelines** for complex data analysis
- **Real-time statistics** and metrics
- **Performance monitoring** with query explanation
- **Data visualization** with interactive charts

### Transactions
- **Atomic ticket purchasing** with seat reservation
- **Rollback support** for failed operations
- **Data consistency** checks and validation
- **Concurrent access** handling

## Development

### Code Quality
```bash
# Format code
black .

# Lint code
ruff check .

# Run tests
pytest
```

### Database Management
```bash
# Generate sample data
python db/seed.py --count 1000

# Create indexes
python db/ensure_indexes.py

# Run transaction demo
python db/transactions_demo.py
```

## Configuration

### Environment Variables
- `DB_TYPE` - Database type (local/cloud)
- `LOCAL_MONGODB_URI` - Local MongoDB connection string
- `CLOUD_MONGODB_URI` - Cloud Atlas connection string
- `LOCAL_DB_NAME` - Local database name
- `CLOUD_DB_NAME` - Cloud database name
- `SECRET_KEY` - Flask secret key
- `FLASK_DEBUG` - Debug mode
- `HOST` - Server host
- `PORT` - Server port

### Database Collections
- `events` - Event information with geospatial data
- `venues` - Venue locations and details
- `users` - User profiles and preferences
- `tickets` - Ticket purchases and status
- `checkins` - Event attendance records

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run linting and formatting
5. Submit a pull request

## License

This project is licensed under the MIT License.
