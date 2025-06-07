import pytest
from datetime import datetime, timedelta
from src.models import Event, EventSource
from src.aggregator import deduplicate, process, hash_title

def create_test_event(
    title: str,
    start_dt: datetime,
    duration_hours: float = 2.0,
    is_all_day: bool = False
) -> Event:
    return Event(
        title=title,
        description="Test event",
        start_dt=start_dt,
        end_dt=start_dt + timedelta(hours=duration_hours),
        location="Montreal",
        url="https://example.com",
        source=EventSource.TOURISME_MTL,
        source_id="test-1",
        is_all_day=is_all_day
    )

def test_hash_title():
    """Test that hash_title creates consistent hashes."""
    # Same title should produce same hash
    hash1 = hash_title("Test Event", datetime(2024, 3, 15))
    hash2 = hash_title("Test Event", datetime(2024, 3, 15))
    assert hash1 == hash2

    # Different title should produce different hash
    hash3 = hash_title("Test Event 2", datetime(2024, 3, 15))
    assert hash1 != hash3

def test_deduplicate():
    """Test that deduplicate removes duplicate events."""
    base_time = datetime.now()
    
    # Create some duplicate events
    events = [
        create_test_event("Event 1", base_time),
        create_test_event("Event 1", base_time),  # Duplicate
        create_test_event("Event 2", base_time),
        create_test_event("Event 1", base_time + timedelta(days=1)),  # Same title, different day
    ]
    
    unique = deduplicate(events)
    assert len(unique) == 3  # Should remove one duplicate

def test_process_separates_festivals():
    """Test that process separates festivals from regular events."""
    base_time = datetime.now()
    
    events = [
        create_test_event("Festival 1", base_time, is_all_day=True),
        create_test_event("Regular Event", base_time),
        create_test_event("Festival 2", base_time, is_all_day=True),
    ]
    
    festivals, curated = process(events)
    assert len(festivals) == 2
    assert len(curated) == 1
    assert all(f.is_all_day for f in festivals)
    assert not any(c.is_all_day for c in curated)

def test_process_daily_cap():
    """Test that process respects daily event cap."""
    base_time = datetime.now()
    
    # Create more than MAX_PER_DAY events for the same day
    events = [
        create_test_event(f"Event {i}", base_time + timedelta(hours=i))
        for i in range(10)  # More than MAX_PER_DAY (5)
    ]
    
    _, curated = process(events)
    assert len(curated) == 5  # Should be capped at MAX_PER_DAY

def test_process_overlap_guardrail():
    """Test that process respects maximum parallel events."""
    base_time = datetime.now()
    
    # Create overlapping events
    events = [
        create_test_event("Event 1", base_time, duration_hours=3),
        create_test_event("Event 2", base_time + timedelta(hours=1), duration_hours=3),
        create_test_event("Event 3", base_time + timedelta(hours=2), duration_hours=3),
        create_test_event("Event 4", base_time + timedelta(hours=2.5), duration_hours=3),
    ]
    
    _, curated = process(events)
    assert len(curated) == 3  # Should be capped at MAX_PARALLEL (3) 