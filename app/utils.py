"""
Utility functions for the EventSphere application.
"""

from datetime import datetime, timedelta, timezone
from typing import Tuple


def calculate_weekend_window(reference_date: datetime = None) -> Tuple[datetime, datetime]:
    """
    Calculate the weekend window (Friday 6pm UTC → Sunday 11:59pm UTC).
    
    The weekend window is defined as:
    - Start: Friday 6:00 PM UTC
    - End: Sunday 11:59 PM UTC
    
    If the reference date is already within a weekend window (Friday 6pm or later),
    it returns the next weekend window.
    
    Args:
        reference_date: The reference date to calculate from. Defaults to current UTC time.
        
    Returns:
        Tuple of (friday_start, sunday_end) datetime objects in UTC
        
    Examples:
        # If called on Monday, returns this Friday 6pm to Sunday 11:59pm
        friday, sunday = calculate_weekend_window()
        
        # If called on Friday 5pm, returns this Friday 6pm to Sunday 11:59pm
        friday, sunday = calculate_weekend_window()
        
        # If called on Friday 7pm, returns next Friday 6pm to Sunday 11:59pm
        friday, sunday = calculate_weekend_window()
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)
    
    # Find the next Friday
    # weekday() returns 0=Monday, 1=Tuesday, ..., 4=Friday, 5=Saturday, 6=Sunday
    days_until_friday = (4 - reference_date.weekday()) % 7
    
    # If it's Friday and it's already 6pm or later, get next Friday
    if days_until_friday == 0 and reference_date.hour >= 18:
        days_until_friday = 7
    
    # Calculate Friday 6:00 PM UTC
    friday_start = reference_date.replace(
        hour=18, 
        minute=0, 
        second=0, 
        microsecond=0
    ) + timedelta(days=days_until_friday)
    
    # Calculate Sunday 11:59 PM UTC (2 days and 5 hours 59 minutes after Friday 6pm)
    sunday_end = friday_start + timedelta(days=2, hours=5, minutes=59)
    
    return friday_start, sunday_end


def is_within_weekend_window(check_date: datetime, reference_date: datetime = None) -> bool:
    """
    Check if a given date falls within the weekend window.
    
    Args:
        check_date: The date to check
        reference_date: The reference date to calculate the weekend window from
        
    Returns:
        True if the check_date falls within the weekend window, False otherwise
    """
    friday_start, sunday_end = calculate_weekend_window(reference_date)
    return friday_start <= check_date <= sunday_end


def get_weekend_window_info(reference_date: datetime = None) -> dict:
    """
    Get detailed information about the weekend window.
    
    Args:
        reference_date: The reference date to calculate the weekend window from
        
    Returns:
        Dictionary with weekend window information including:
        - start: Friday 6pm UTC
        - end: Sunday 11:59pm UTC
        - duration_hours: Total duration in hours
        - duration_days: Total duration in days
        - is_currently_weekend: Whether the reference date is within the weekend window
    """
    friday_start, sunday_end = calculate_weekend_window(reference_date)
    duration = sunday_end - friday_start
    
    return {
        "start": friday_start,
        "end": sunday_end,
        "duration_hours": duration.total_seconds() / 3600,
        "duration_days": duration.days + duration.seconds / 86400,
        "is_currently_weekend": is_within_weekend_window(reference_date or datetime.now(timezone.utc), reference_date)
    }
