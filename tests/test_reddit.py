import pytest
from unittest.mock import patch
from src.sources.reddit import get_reddit_events
from src.models import EventSource

SAMPLE_RESPONSE = {
    "data": {
        "children": [
            {
                "data": {
                    "id": "abc123",
                    "selftext": "Mar 28 | Reddit Event | Mile End | https://reddit.com/event/1\nMar 29 | Another Event | Downtown | https://reddit.com/event/2",
                    "url": "https://reddit.com/r/montreal/thread/abc123"
                }
            }
        ]
    }
}

@pytest.fixture
def mock_response():
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = SAMPLE_RESPONSE
        mock_get.return_value.raise_for_status.return_value = None
        yield mock_get

def test_get_reddit_events(mock_response):
    events = get_reddit_events()
    mock_response.assert_called_once()
    assert len(events) == 2
    assert events[0].title == "Reddit Event"
    assert events[0].source == EventSource.REDDIT
    assert events[0].location == "Mile End"
    assert events[0].url == "https://reddit.com/event/1"
    assert events[1].title == "Another Event"
    assert events[1].location == "Downtown" 