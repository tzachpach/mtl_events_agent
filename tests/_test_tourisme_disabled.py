import pytest
from unittest.mock import patch
from src.sources import tourisme
from src.models import EventSource

SAMPLE_RESPONSE = {
    "data": [
        {
            "id": 42,
            "title": "Tourisme Festival",
            "description": "A fun festival!",
            "start_date": "2024-03-28T00:00:00",
            "end_date": "2024-03-30T23:59:59",
            "location": "Old Port",
            "url": "https://mtl.org/event/42"
        }
    ]
}

@pytest.fixture
def mock_response():
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = SAMPLE_RESPONSE
        mock_get.return_value.raise_for_status.return_value = None
        yield mock_get

def test_get_tourisme_events(mock_response):
    events = tourisme.get_tourisme_events()
    mock_response.assert_called_once()
    assert len(events) == 1
    event = events[0]
    assert event.title == "Tourisme Festival"
    assert event.source == EventSource.TOURISME_MTL
    assert event.source_id == "42"
    assert event.location == "Old Port"
    assert event.is_all_day

def test_get_tourisme_events():
    dummy_event = {
        "id": 1,
        "title": "Test Event",
        "description": "A test event.",
        "start_date": "2099-07-01T18:00:00",
        "end_date": "2099-07-01T20:00:00",
        "location": "Test Location",
        "url": "http://example.com"
    }
    mock_response = type('Response', (), {'json': lambda: {"data": [dummy_event]}, 'raise_for_status': lambda: None})
    with patch('requests.get', return_value=mock_response):
        events = tourisme.get_tourisme_events()
        assert len(events) == 1 