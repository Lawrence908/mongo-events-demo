"""
Unit tests for EVE-10: Weekend window calculation utility.

Tests boundary conditions and edge cases for the weekend window calculation.
"""

import unittest
from datetime import datetime, timedelta
from app.utils import calculate_weekend_window, is_within_weekend_window, get_weekend_window_info


class TestWeekendWindowCalculation(unittest.TestCase):
    """Test cases for weekend window calculation utility."""

    def test_monday_reference(self):
        """Test weekend calculation when reference date is Monday."""
        # Monday, January 8, 2024 at 10:00 AM UTC
        monday = datetime(2024, 1, 8, 10, 0, 0)
        friday_start, sunday_end = calculate_weekend_window(monday)
        
        # Should return Friday, January 12, 2024 at 6:00 PM UTC
        expected_friday = datetime(2024, 1, 12, 18, 0, 0)
        # Should return Sunday, January 14, 2024 at 11:59 PM UTC
        expected_sunday = datetime(2024, 1, 14, 23, 59, 0)
        
        self.assertEqual(friday_start, expected_friday)
        self.assertEqual(sunday_end, expected_sunday)

    def test_tuesday_reference(self):
        """Test weekend calculation when reference date is Tuesday."""
        # Tuesday, January 9, 2024 at 2:00 PM UTC
        tuesday = datetime(2024, 1, 9, 14, 0, 0)
        friday_start, sunday_end = calculate_weekend_window(tuesday)
        
        # Should return Friday, January 12, 2024 at 6:00 PM UTC
        expected_friday = datetime(2024, 1, 12, 18, 0, 0)
        expected_sunday = datetime(2024, 1, 14, 23, 59, 0)
        
        self.assertEqual(friday_start, expected_friday)
        self.assertEqual(sunday_end, expected_sunday)

    def test_wednesday_reference(self):
        """Test weekend calculation when reference date is Wednesday."""
        # Wednesday, January 10, 2024 at 9:00 AM UTC
        wednesday = datetime(2024, 1, 10, 9, 0, 0)
        friday_start, sunday_end = calculate_weekend_window(wednesday)
        
        # Should return Friday, January 12, 2024 at 6:00 PM UTC
        expected_friday = datetime(2024, 1, 12, 18, 0, 0)
        expected_sunday = datetime(2024, 1, 14, 23, 59, 0)
        
        self.assertEqual(friday_start, expected_friday)
        self.assertEqual(sunday_end, expected_sunday)

    def test_thursday_reference(self):
        """Test weekend calculation when reference date is Thursday."""
        # Thursday, January 11, 2024 at 3:00 PM UTC
        thursday = datetime(2024, 1, 11, 15, 0, 0)
        friday_start, sunday_end = calculate_weekend_window(thursday)
        
        # Should return Friday, January 12, 2024 at 6:00 PM UTC
        expected_friday = datetime(2024, 1, 12, 18, 0, 0)
        expected_sunday = datetime(2024, 1, 14, 23, 59, 0)
        
        self.assertEqual(friday_start, expected_friday)
        self.assertEqual(sunday_end, expected_sunday)

    def test_friday_before_6pm(self):
        """Test weekend calculation when reference date is Friday before 6pm."""
        # Friday, January 12, 2024 at 5:59 PM UTC
        friday_before = datetime(2024, 1, 12, 17, 59, 0)
        friday_start, sunday_end = calculate_weekend_window(friday_before)
        
        # Should return this Friday at 6:00 PM UTC
        expected_friday = datetime(2024, 1, 12, 18, 0, 0)
        expected_sunday = datetime(2024, 1, 14, 23, 59, 0)
        
        self.assertEqual(friday_start, expected_friday)
        self.assertEqual(sunday_end, expected_sunday)

    def test_friday_at_6pm(self):
        """Test weekend calculation when reference date is Friday exactly at 6pm."""
        # Friday, January 12, 2024 at 6:00 PM UTC
        friday_at_6pm = datetime(2024, 1, 12, 18, 0, 0)
        friday_start, sunday_end = calculate_weekend_window(friday_at_6pm)
        
        # Should return next Friday at 6:00 PM UTC (since it's already 6pm)
        expected_friday = datetime(2024, 1, 19, 18, 0, 0)
        expected_sunday = datetime(2024, 1, 21, 23, 59, 0)
        
        self.assertEqual(friday_start, expected_friday)
        self.assertEqual(sunday_end, expected_sunday)

    def test_friday_after_6pm(self):
        """Test weekend calculation when reference date is Friday after 6pm."""
        # Friday, January 12, 2024 at 7:30 PM UTC
        friday_after = datetime(2024, 1, 12, 19, 30, 0)
        friday_start, sunday_end = calculate_weekend_window(friday_after)
        
        # Should return next Friday at 6:00 PM UTC
        expected_friday = datetime(2024, 1, 19, 18, 0, 0)
        expected_sunday = datetime(2024, 1, 21, 23, 59, 0)
        
        self.assertEqual(friday_start, expected_friday)
        self.assertEqual(sunday_end, expected_sunday)

    def test_saturday_reference(self):
        """Test weekend calculation when reference date is Saturday."""
        # Saturday, January 13, 2024 at 2:00 PM UTC
        saturday = datetime(2024, 1, 13, 14, 0, 0)
        friday_start, sunday_end = calculate_weekend_window(saturday)
        
        # Should return next Friday at 6:00 PM UTC
        expected_friday = datetime(2024, 1, 19, 18, 0, 0)
        expected_sunday = datetime(2024, 1, 21, 23, 59, 0)
        
        self.assertEqual(friday_start, expected_friday)
        self.assertEqual(sunday_end, expected_sunday)

    def test_sunday_reference(self):
        """Test weekend calculation when reference date is Sunday."""
        # Sunday, January 14, 2024 at 10:00 AM UTC
        sunday = datetime(2024, 1, 14, 10, 0, 0)
        friday_start, sunday_end = calculate_weekend_window(sunday)
        
        # Should return next Friday at 6:00 PM UTC
        expected_friday = datetime(2024, 1, 19, 18, 0, 0)
        expected_sunday = datetime(2024, 1, 21, 23, 59, 0)
        
        self.assertEqual(friday_start, expected_friday)
        self.assertEqual(sunday_end, expected_sunday)

    def test_sunday_at_11_59pm(self):
        """Test weekend calculation when reference date is Sunday at 11:59pm."""
        # Sunday, January 14, 2024 at 11:59 PM UTC
        sunday_late = datetime(2024, 1, 14, 23, 59, 0)
        friday_start, sunday_end = calculate_weekend_window(sunday_late)
        
        # Should return next Friday at 6:00 PM UTC
        expected_friday = datetime(2024, 1, 19, 18, 0, 0)
        expected_sunday = datetime(2024, 1, 21, 23, 59, 0)
        
        self.assertEqual(friday_start, expected_friday)
        self.assertEqual(sunday_end, expected_sunday)

    def test_weekend_duration(self):
        """Test that weekend window duration is correct."""
        # Any reference date
        reference = datetime(2024, 1, 8, 10, 0, 0)
        friday_start, sunday_end = calculate_weekend_window(reference)
        
        # Duration should be 2 days, 5 hours, 59 minutes
        duration = sunday_end - friday_start
        expected_duration = timedelta(days=2, hours=5, minutes=59)
        
        self.assertEqual(duration, expected_duration)

    def test_weekend_window_info(self):
        """Test the weekend window info function."""
        reference = datetime(2024, 1, 8, 10, 0, 0)  # Monday
        info = get_weekend_window_info(reference)
        
        self.assertIn("start", info)
        self.assertIn("end", info)
        self.assertIn("duration_hours", info)
        self.assertIn("duration_days", info)
        self.assertIn("is_currently_weekend", info)
        
        # Should not be currently weekend on Monday
        self.assertFalse(info["is_currently_weekend"])
        
        # Duration should be approximately 53.98 hours (2 days, 5 hours, 59 minutes)
        self.assertAlmostEqual(info["duration_hours"], 53.98, places=1)

    def test_is_within_weekend_window(self):
        """Test the is_within_weekend_window function."""
        # Reference: Monday
        reference = datetime(2024, 1, 8, 10, 0, 0)
        
        # Friday 6pm should be within weekend window
        friday_6pm = datetime(2024, 1, 12, 18, 0, 0)
        self.assertTrue(is_within_weekend_window(friday_6pm, reference))
        
        # Saturday should be within weekend window
        saturday = datetime(2024, 1, 13, 14, 0, 0)
        self.assertTrue(is_within_weekend_window(saturday, reference))
        
        # Sunday 11:59pm should be within weekend window
        sunday_late = datetime(2024, 1, 14, 23, 59, 0)
        self.assertTrue(is_within_weekend_window(sunday_late, reference))
        
        # Monday should not be within weekend window
        monday = datetime(2024, 1, 15, 10, 0, 0)
        self.assertFalse(is_within_weekend_window(monday, reference))
        
        # Friday 5:59pm should not be within weekend window
        friday_before = datetime(2024, 1, 12, 17, 59, 0)
        self.assertFalse(is_within_weekend_window(friday_before, reference))

    def test_edge_case_friday_5_59_59(self):
        """Test edge case: Friday at 5:59:59 PM."""
        friday_almost_6pm = datetime(2024, 1, 12, 17, 59, 59)
        friday_start, sunday_end = calculate_weekend_window(friday_almost_6pm)
        
        # Should return this Friday at 6:00 PM UTC
        expected_friday = datetime(2024, 1, 12, 18, 0, 0)
        expected_sunday = datetime(2024, 1, 14, 23, 59, 0)
        
        self.assertEqual(friday_start, expected_friday)
        self.assertEqual(sunday_end, expected_sunday)

    def test_edge_case_friday_6_00_01(self):
        """Test edge case: Friday at 6:00:01 PM."""
        friday_just_after_6pm = datetime(2024, 1, 12, 18, 0, 1)
        friday_start, sunday_end = calculate_weekend_window(friday_just_after_6pm)
        
        # Should return next Friday at 6:00 PM UTC
        expected_friday = datetime(2024, 1, 19, 18, 0, 0)
        expected_sunday = datetime(2024, 1, 21, 23, 59, 0)
        
        self.assertEqual(friday_start, expected_friday)
        self.assertEqual(sunday_end, expected_sunday)

    def test_year_boundary(self):
        """Test weekend calculation across year boundary."""
        # December 30, 2023 (Monday)
        dec_30 = datetime(2023, 12, 30, 10, 0, 0)
        friday_start, sunday_end = calculate_weekend_window(dec_30)
        
        # Should return January 5, 2024 at 6:00 PM UTC
        expected_friday = datetime(2024, 1, 5, 18, 0, 0)
        expected_sunday = datetime(2024, 1, 7, 23, 59, 0)
        
        self.assertEqual(friday_start, expected_friday)
        self.assertEqual(sunday_end, expected_sunday)

    def test_leap_year_february(self):
        """Test weekend calculation in leap year February."""
        # February 28, 2024 (Wednesday) - leap year
        feb_28 = datetime(2024, 2, 28, 10, 0, 0)
        friday_start, sunday_end = calculate_weekend_window(feb_28)
        
        # Should return March 1, 2024 at 6:00 PM UTC
        expected_friday = datetime(2024, 3, 1, 18, 0, 0)
        expected_sunday = datetime(2024, 3, 3, 23, 59, 0)
        
        self.assertEqual(friday_start, expected_friday)
        self.assertEqual(sunday_end, expected_sunday)

    def test_default_reference_date(self):
        """Test that function works with default reference date (current time)."""
        # This test ensures the function doesn't crash with default parameters
        friday_start, sunday_end = calculate_weekend_window()
        
        # Should return valid datetime objects
        self.assertIsInstance(friday_start, datetime)
        self.assertIsInstance(sunday_end, datetime)
        
        # Friday should be before Sunday
        self.assertLess(friday_start, sunday_end)
        
        # Friday should be at 6:00 PM
        self.assertEqual(friday_start.hour, 18)
        self.assertEqual(friday_start.minute, 0)
        self.assertEqual(friday_start.second, 0)
        self.assertEqual(friday_start.microsecond, 0)
        
        # Sunday should be at 11:59 PM
        self.assertEqual(sunday_end.hour, 23)
        self.assertEqual(sunday_end.minute, 59)
        self.assertEqual(sunday_end.second, 0)
        self.assertEqual(sunday_end.microsecond, 0)


if __name__ == "__main__":
    unittest.main()
