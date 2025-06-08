import pytest
from datetime import datetime, date, time, timedelta
import pytz
from src.models import Event, MONTREAL_TZ

# Helper to create timezone-aware datetime objects for testing
def montreal_dt(*args, **kwargs):
    return MONTREAL_TZ.localize(datetime(*args, **kwargs))

# Test cases for Event.parse_date
@pytest.mark.parametrize("dt_str, expected_dt", [
    # ISO 8601 with timezone
    ("2024-03-15T10:00:00-05:00", montreal_dt(2024, 3, 15, 10, 0, 0)),
    ("2024-03-15T10:00:00-04:00", montreal_dt(2024, 3, 15, 9, 0, 0)), # DST difference
    
    # ISO 8601 without timezone (assumed Montreal)
    ("2024-03-15T10:00:00", montreal_dt(2024, 3, 15, 10, 0, 0)),
    
    # Date only (assumed midnight Montreal time)
    ("2024-03-15", montreal_dt(2024, 3, 15, 0, 0, 0)),
    
    # Common combined format (YYYY-MM-DD HH:MM:SS)
    ("2024-03-15 10:00:00", montreal_dt(2024, 3, 15, 10, 0, 0)),
    
    # Test DST transition (Spring forward) - March 10, 2024
    ("2024-03-10T01:30:00", montreal_dt(2024, 3, 10, 1, 30, 0, tzinfo=pytz.timezone('America/Montreal'))), # Before DST change
    ("2024-03-10T03:30:00", montreal_dt(2024, 3, 10, 3, 30, 0, tzinfo=pytz.timezone('America/Montreal'))), # After DST change (2AM becomes 3AM)

    # Test DST transition (Fall back) - November 3, 2024
    ("2024-11-03T01:30:00", montreal_dt(2024, 11, 3, 1, 30, 0, tzinfo=pytz.timezone('America/Montreal'))), # First pass of 1:30 AM
    ("2024-11-03T01:30:00-05:00", montreal_dt(2024, 11, 3, 1, 30, 0, tzinfo=pytz.timezone('America/Montreal'))), # Second pass of 1:30 AM (explicitly -05:00)

    # Edge case: empty string
    # This case is handled by a ValueError, so not in parametrize
])
def test_parse_date_success(dt_str, expected_dt):
    parsed_dt = Event.parse_date(dt_str)
    assert parsed_dt == expected_dt
    assert parsed_dt.tzinfo is not None
    assert parsed_dt.tzinfo.tzname(parsed_dt) in ['EST', 'EDT'] # Should be EST or EDT for Montreal

def test_parse_date_empty_string():
    with pytest.raises(ValueError, match="Date string cannot be empty"):
        Event.parse_date("")

def test_parse_date_invalid_format():
    with pytest.raises(ValueError, match="Could not parse date string"):
        Event.parse_date("invalid-date-string") 