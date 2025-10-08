# Test Suite for EventSphere

This directory contains comprehensive tests for the EventSphere application, all updated to use camelCase field names as required.

## Test Structure

### Essential Tests (Run First)
- **`test_comprehensive_camelcase.py`** - Main comprehensive test suite covering all core functionality
- **`test_eve5_eve7_schema_crud.py`** - Schema validation and CRUD operations
- **`test_performance.py`** - Performance testing with large datasets

### Specialized Tests
- **`test_reviews.py`** - Review and rating system tests
- **`test_enhanced_checkins.py`** - Check-in functionality tests
- **`test_eve8_text_search.py`** - Text search functionality
- **`test_eve9_cursor_pagination.py`** - Cursor-based pagination
- **`test_eve11_nearby_api.py`** - Geospatial nearby events API
- **`test_eve12_weekend_api.py`** - Weekend events discovery
- **`test_eve13_category_geo_compound.py`** - Compound geospatial queries
- **`test_eve38_geocoding.py`** - Geocoding functionality
- **`test_eve6_indexes.py`** - Database index testing

### Test Runners
- **`run_essential_tests.py`** - Run the most important tests
- **`run_eve12_test.py`** - Run specific EVE-12 tests

## Running Tests

### Quick Test (Recommended)
```bash
python tests/run_essential_tests.py
```

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test
```bash
pytest tests/test_comprehensive_camelcase.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

## Test Data

Tests use a separate test database (`test_events_demo`) and clean up after each test run. No production data is affected.

## camelCase Field Names

All tests have been updated to use camelCase field names as required:

- `startDate` instead of `start_date`
- `eventType` instead of `event_type`
- `venueType` instead of `venue_type`
- `userId` instead of `user_id`
- `eventId` instead of `event_id`
- `venueId` instead of `venue_id`
- `qrCode` instead of `qr_code`
- `ticketTier` instead of `ticket_tier`
- `checkInTime` instead of `check_in_time`
- `firstName` instead of `first_name`
- `lastName` instead of `last_name`
- `createdAt` instead of `created_at`
- `updatedAt` instead of `updated_at`
- And many more...

## Test Categories

### 1. Model Validation Tests
- Test Pydantic model validation
- Test field constraints and validation rules
- Test camelCase field mapping

### 2. API Endpoint Tests
- Test HTTP endpoints
- Test request/response handling
- Test error handling

### 3. Database Operation Tests
- Test CRUD operations
- Test data persistence
- Test data retrieval

### 4. Geospatial Tests
- Test location-based queries
- Test nearby events discovery
- Test geospatial indexing

### 5. Performance Tests
- Test with large datasets
- Test query performance
- Test indexing effectiveness

### 6. Integration Tests
- Test end-to-end workflows
- Test service interactions
- Test data consistency

## Troubleshooting

### Common Issues
1. **Database Connection**: Ensure MongoDB is running
2. **Environment Variables**: Check MONGODB_URI and MONGODB_DB_NAME
3. **Field Name Mismatches**: Ensure all snake_case has been converted to camelCase
4. **Import Errors**: Check Python path and module imports

### Debug Mode
```bash
pytest tests/ -v -s --tb=long
```

### Test Specific Functionality
```bash
pytest tests/test_comprehensive_camelcase.py::TestModels::test_event_create_valid -v
```

## Contributing

When adding new tests:
1. Use camelCase field names consistently
2. Follow the existing test structure
3. Add appropriate docstrings
4. Include both positive and negative test cases
5. Clean up test data after each test
