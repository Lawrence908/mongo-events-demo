# EVE-10 Report: Weekend Window Calculation Utility

**Ticket**: EVE-10 - Weekend window calculation util  
**Priority**: 3  
**Estimate**: 2h  
**Status**: ✅ COMPLETED  
**Dependencies**: EVE-7 (CRUD services parity and unit tests)

## Summary

Successfully implemented a standalone weekend window calculation utility that computes Friday 6pm → Sunday 11:59pm in UTC. The utility includes comprehensive unit tests covering all boundary conditions and edge cases, ensuring robust date/time calculations for weekend event discovery.

## Acceptance Criteria Status

### ✅ Covered by unit tests for boundary conditions
- **Test Coverage**: 18 comprehensive test cases covering all boundary conditions
- **Edge Cases**: Friday 5:59:59 PM, Friday 6:00:01 PM, year boundaries, leap years
- **Day Coverage**: All days of the week (Monday through Sunday)
- **Time Coverage**: Various times throughout the day, including exact boundary conditions
- **Duration Validation**: Correct weekend window duration (2 days, 5 hours, 59 minutes)

## Technical Implementation

### 1. Utility Module (`app/utils.py`)
- **Main Function**: `calculate_weekend_window(reference_date=None)`
- **Helper Functions**: `is_within_weekend_window()`, `get_weekend_window_info()`
- **Logic**: Calculates Friday 6:00 PM UTC to Sunday 11:59 PM UTC
- **Edge Handling**: If reference date is Friday 6pm or later, returns next weekend window

### 2. Service Integration (`app/services.py`)
- **Refactored**: `get_events_this_weekend()` method now uses the utility function
- **Cleaner Code**: Removed inline weekend calculation logic
- **Consistency**: Ensures all weekend calculations use the same logic

### 3. Comprehensive Test Suite (`tests/test_eve10_weekend_window.py`)
- **18 Test Cases**: Covering all possible scenarios and edge cases
- **Boundary Testing**: Exact time boundaries (5:59:59 PM vs 6:00:01 PM)
- **Day Testing**: All days of the week as reference dates
- **Edge Cases**: Year boundaries, leap years, microsecond precision
- **Validation**: Duration, time accuracy, and logical correctness

## Code Implementation

### Weekend Window Calculation Logic
```python
def calculate_weekend_window(reference_date: datetime = None) -> Tuple[datetime, datetime]:
    """
    Calculate the weekend window (Friday 6pm UTC → Sunday 11:59pm UTC).
    
    The weekend window is defined as:
    - Start: Friday 6:00 PM UTC
    - End: Sunday 11:59 PM UTC
    
    If the reference date is already within a weekend window (Friday 6pm or later),
    it returns the next weekend window.
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)
    
    # Find the next Friday
    days_until_friday = (4 - reference_date.weekday()) % 7
    
    # If it's Friday and it's already 6pm or later, get next Friday
    if days_until_friday == 0 and reference_date.hour >= 18:
        days_until_friday = 7
    
    # Calculate Friday 6:00 PM UTC
    friday_start = reference_date.replace(
        hour=18, minute=0, second=0, microsecond=0
    ) + timedelta(days=days_until_friday)
    
    # Calculate Sunday 11:59 PM UTC
    sunday_end = friday_start + timedelta(days=2, hours=5, minutes=59)
    
    return friday_start, sunday_end
```

### Service Integration
```python
def get_events_this_weekend(self, longitude: float, latitude: float, radius_km: float = 50) -> dict[str, Any]:
    """Get events this weekend near a location - perfect for your use case!"""
    db = self._ensure_db()
    
    # Calculate weekend date range using the utility function
    friday, sunday = calculate_weekend_window()
    
    # ... rest of the method uses friday and sunday variables
```

## Test Results

### Test Coverage Summary
- **Total Tests**: 18 test cases
- **All Tests Pass**: ✅ 100% success rate
- **Coverage Areas**:
  - All days of the week as reference dates
  - Boundary conditions (Friday 5:59:59 PM vs 6:00:01 PM)
  - Edge cases (year boundaries, leap years)
  - Duration validation
  - Helper function testing

### Key Test Cases
1. **Monday Reference**: Returns this Friday 6pm to Sunday 11:59pm
2. **Friday Before 6pm**: Returns this Friday 6pm to Sunday 11:59pm
3. **Friday At 6pm**: Returns next Friday 6pm to Sunday 11:59pm
4. **Friday After 6pm**: Returns next Friday 6pm to Sunday 11:59pm
5. **Weekend Days**: Returns next Friday 6pm to Sunday 11:59pm
6. **Edge Cases**: Microsecond precision, year boundaries, leap years

### Test Execution Results
```bash
$ python -m pytest tests/test_eve10_weekend_window.py -v
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-7.4.4, pluggy-1.6.0
collected 18 items

tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_default_reference_date PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_edge_case_friday_5_59_59 PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_edge_case_friday_6_00_01 PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_friday_after_6pm PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_friday_at_6pm PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_friday_before_6pm PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_is_within_weekend_window PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_leap_year_february PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_monday_reference PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_saturday_reference PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_sunday_at_11_59pm PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_sunday_reference PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_thursday_reference PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_tuesday_reference PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_wednesday_reference PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_weekend_duration PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_weekend_window_info PASSED
tests/test_eve10_weekend_window.py::TestWeekendWindowCalculation::test_year_boundary PASSED

============================== 18 passed in 5.58s ==============================
```

**Note**: The initial implementation had a deprecation warning for `datetime.utcnow()`, which has been resolved by updating to use `datetime.now(timezone.utc)` for Python 3.12+ compatibility.
```

## API Usage Examples

### Basic Weekend Window Calculation
```python
from app.utils import calculate_weekend_window

# Get current weekend window
friday_start, sunday_end = calculate_weekend_window()
print(f"Weekend starts: {friday_start}")
print(f"Weekend ends: {sunday_end}")
```

### Check if Date is Within Weekend Window
```python
from app.utils import is_within_weekend_window
from datetime import datetime

# Check if a specific date is within the weekend window
check_date = datetime(2024, 1, 13, 14, 0, 0)  # Saturday 2pm
is_weekend = is_within_weekend_window(check_date)
print(f"Is weekend: {is_weekend}")
```

### Get Detailed Weekend Window Information
```python
from app.utils import get_weekend_window_info

# Get comprehensive weekend window information
info = get_weekend_window_info()
print(f"Start: {info['start']}")
print(f"End: {info['end']}")
print(f"Duration: {info['duration_hours']} hours")
print(f"Currently weekend: {info['is_currently_weekend']}")
```

### Service Integration
```python
from app.services import get_event_service

# Get events this weekend (uses the utility internally)
service = get_event_service()
weekend_events = service.get_events_this_weekend(
    longitude=-74.0060,  # NYC
    latitude=40.7128,
    radius_km=50
)
```

## Boundary Conditions Tested

### Time Boundaries
- **Friday 5:59:59 PM**: Returns this Friday 6pm to Sunday 11:59pm
- **Friday 6:00:00 PM**: Returns next Friday 6pm to Sunday 11:59pm
- **Friday 6:00:01 PM**: Returns next Friday 6pm to Sunday 11:59pm

### Day Boundaries
- **Monday**: Returns this Friday 6pm to Sunday 11:59pm
- **Tuesday**: Returns this Friday 6pm to Sunday 11:59pm
- **Wednesday**: Returns this Friday 6pm to Sunday 11:59pm
- **Thursday**: Returns this Friday 6pm to Sunday 11:59pm
- **Friday (before 6pm)**: Returns this Friday 6pm to Sunday 11:59pm
- **Friday (6pm or later)**: Returns next Friday 6pm to Sunday 11:59pm
- **Saturday**: Returns next Friday 6pm to Sunday 11:59pm
- **Sunday**: Returns next Friday 6pm to Sunday 11:59pm

### Special Cases
- **Year Boundaries**: December 30, 2023 → January 5, 2024 weekend
- **Leap Year February**: February 28, 2024 → March 1, 2024 weekend
- **Duration Validation**: Exactly 2 days, 5 hours, 59 minutes

## Dependencies Satisfied

- **EVE-7**: CRUD services provide the foundation for weekend event discovery functionality

## Future Enhancements

1. **Timezone Support**: Extend utility to support different timezones
2. **Custom Weekend Definition**: Allow configurable weekend start/end times
3. **Holiday Awareness**: Consider holidays that might affect weekend definitions
4. **Performance Optimization**: Cache weekend calculations for repeated calls

## Conclusion

EVE-10 has been successfully implemented with all acceptance criteria met. The weekend window calculation utility provides:

- ✅ Standalone utility function for weekend window calculation
- ✅ Comprehensive unit test coverage for all boundary conditions
- ✅ Clean integration with existing service layer
- ✅ Robust handling of edge cases and time boundaries
- ✅ Well-documented API with usage examples
- ✅ 100% test pass rate with 18 test cases

The implementation is production-ready and provides a solid foundation for weekend event discovery features. The utility is reusable across the application and ensures consistent weekend window calculations throughout the system.
