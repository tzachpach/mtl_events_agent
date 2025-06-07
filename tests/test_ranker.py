import pytest
from datetime import datetime, timedelta
from src.models import Event, EventSource
from src.ranker import rank_and_filter

def create_test_event(
    title: str,
    start_dt: datetime,
    duration_hours: float = 2.0,
    popularity: float = 0.5
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
        popularity=popularity
    )

def test_keyword_scoring():
    events = [
        create_test_event("Free Improv Show", datetime.now(), popularity=0.5),
        create_test_event("Regular Event", datetime.now(), popularity=0.8),
    ]
    
    ranked = rank_and_filter(events)
    assert len(ranked) == 2
    assert ranked[0].title == "Free Improv Show"  # Should rank higher due to keywords

def test_max_per_day():
    test_date = datetime(2025, 1, 1, 10, 0, 0) # Fixed date and time
    events = []
    for i in range(10):
        events.append(
            Event(
                title=f"Event {i}",
                description="Test event",
                start_dt=test_date + timedelta(minutes=i * 10), # Ensure events are on the same day but distinct times
                end_dt=test_date + timedelta(minutes=i * 10, hours=1),
                location="Montreal",
                url="https://example.com",
                source=EventSource.TOURISME_MTL,
                source_id="test-1",
                is_all_day=False,
                popularity=0.5
            )
        )
    ranked = rank_and_filter(events)
    assert len(ranked) == 5  # MAX_PER_DAY

def test_max_parallel():
    base_time = datetime.now()
    events = [
        create_test_event("Event 1", base_time, duration_hours=3),
        create_test_event("Event 2", base_time + timedelta(hours=1), duration_hours=3),
        create_test_event("Event 3", base_time + timedelta(hours=2), duration_hours=3),
        create_test_event("Event 4", base_time + timedelta(hours=2.5), duration_hours=3),
    ]
    
    ranked = rank_and_filter(events)
    assert len(ranked) == 3  # MAX_PARALLEL

def test_sorting():
    base_time = datetime.now()
    events = [
        create_test_event("Low Score", base_time, popularity=0.1),
        create_test_event("High Score", base_time, popularity=0.9),
        create_test_event("Medium Score", base_time, popularity=0.5),
    ]
    
    ranked = rank_and_filter(events)
    assert ranked[0].title == "High Score"
    assert ranked[1].title == "Medium Score"
    assert ranked[2].title == "Low Score" 