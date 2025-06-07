import os
import pytest
from unittest.mock import patch
from src.sources import ticketmaster
from src.models import EventSource

SAMPLE_RESPONSE = {
    "_embedded": {
        "events": [
            {
                "id": "tm-evt-1",
                "name": "Sample TM Event",
                "info": "A Ticketmaster event.",
                "dates": {
                    "start": {"dateTime": "2024-03-25T20:00:00Z"},
                    "end": {"dateTime": "2024-03-25T22:00:00Z"}
                },
                "url": "https://ticketmaster.com/event/1",
                "_embedded": {
                    "venues": [
                        {"name": "TM Venue"}
                    ]
                }
            }
        ]
    }
}

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {"TICKETMASTER_API_KEY": "test-key"}):
        yield

@pytest.fixture
def mock_response():
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = SAMPLE_RESPONSE
        mock_get.return_value.raise_for_status.return_value = None
        yield mock_get

def test_get_ticketmaster_events(mock_env, mock_response):
    events = ticketmaster.get_ticketmaster_events()
    mock_response.assert_called_once()
    assert len(events) == 1
    event = events[0]
    assert event.title == "Sample TM Event"
    assert event.source == EventSource.TICKETMASTER
    assert event.source_id == "tm-evt-1"
    assert event.location == "TM Venue"
    assert event.popularity is None

def test_get_ticketmaster_events():
    mock_response_json = {
        "_embedded": {
            "events": [
                {
                    "name": "Test Event",
                    "dates": {
                        "start": {"dateTime": "2099-01-01T10:00:00Z"},
                        "end": {"dateTime": "2099-01-01T12:00:00Z"}
                    },
                    "_embedded": {"venues": [{"name": "Test Venue"}]},
                    "url": "http://test.ticketmaster.com",
                    "id": "test-id-1"
                }
            ]
        }
    }
    with patch.dict(os.environ, {"TICKETMASTER_KEY": "dummy_key"}), \
         patch('requests.get', return_value=type('Response', (), {'json': lambda: mock_response_json, 'raise_for_status': lambda: None})):
        events = ticketmaster.get_ticketmaster_events()
        assert isinstance(events, list)
        assert len(events) == 1
        assert events[0].title == "Test Event" 