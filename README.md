# MongoDB Events Demo

A full-stack web application demonstrating MongoDB's geospatial capabilities with event management and mapping features. Built with Flask, PyMongo, and interactive frontend technologies.

## Features

- **Interactive Event Map**: Leaflet.js-powered map showing events with geospatial queries
- **Event Management**: Create, view, edit, and delete events with location-based search
- **RESTful API**: Complete REST API for event operations with GeoJSON support
- **Responsive UI**: Bootstrap 5 with Alpine.js for interactive components
- **Data Validation**: Pydantic models for robust data validation
- **Sample Data**: Faker-based data generation for testing and development

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
- **Alpine.js** - Lightweight JavaScript framework for interactivity
- **Leaflet.js** - Interactive maps with OpenStreetMap tiles

### Development Tools
- **ruff** - Fast Python linter
- **black** - Code formatter
- **pytest** - Testing framework
- **Faker** - Sample data generation

## Prerequisites

- Python 3.11 or higher
- MongoDB server (local or cloud)
- Git

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Lawrence908/mongo-events-demo.git
   cd mongo-events-demo
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB connection details
   ```

5. **Configure MongoDB**
   - Ensure MongoDB is running locally or update `MONGODB_URI` in `.env`
   - The application will automatically create the database and collections

## Usage

### Start the Application

```bash
python run.py
```

The application will be available at `http://127.0.0.1:5000`

### Generate Sample Data

```bash
python data/generate_sample_data.py --count 50
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
# Format code
black .

# Lint code
ruff check .
```

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
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
└── run.py                   # Application entry point
```

## API Endpoints

### Events
- `GET /api/events` - List events with pagination and filtering
- `POST /api/events` - Create new event
- `GET /api/events/<id>` - Get single event
- `PUT /api/events/<id>` - Update event
- `DELETE /api/events/<id>` - Delete event

### Geospatial
- `GET /api/events/nearby` - Find events near coordinates (GeoJSON)
  - Query params: `lat`, `lng`, `radius` (km), `limit`

### Utility
- `GET /api/categories` - List event categories

## Frontend Routes

- `/` - Interactive map view
- `/events` - Events list with filtering
- `/events/new` - Create new event form
- `/events/<id>` - Event details page

## Key Features

### Geospatial Queries
The application uses MongoDB's geospatial features:
- **2dsphere indexes** for location-based queries
- **$geoNear aggregation** for distance-based event search
- **GeoJSON format** for map integration

### Interactive Map
- Click to select location for new events
- Real-time event search with radius control
- Pop-up details for map markers
- Current location detection

### Data Validation
Pydantic models ensure:
- Coordinate validation (lat/lng ranges)
- Date validation (end date after start date)
- Required field enforcement
- Type safety throughout the application

## Testing

Run the test suite:
```bash
# All tests
pytest

# Verbose output
pytest -v

# Specific test file
pytest tests/test_app.py

# Coverage report
pytest --cov=app
```

## Configuration

Environment variables (`.env`):

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=events_demo

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Application Settings
HOST=127.0.0.1
PORT=5000
```

## Sample Data

Generate realistic test data:

```bash
# Generate 50 events (default)
python data/generate_sample_data.py

# Generate custom number of events
python data/generate_sample_data.py --count 100

# Clear existing data first
python data/generate_sample_data.py --clear --count 25
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run linting: `ruff check . && black --check .`
5. Run tests: `pytest`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Enhancements

- [ ] User authentication and event ownership
- [ ] Event categories with custom icons
- [ ] Advanced filtering (date ranges, attendee limits)
- [ ] Event registration system
- [ ] Email notifications
- [ ] Social media integration
- [ ] Mobile PWA support
