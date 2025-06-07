import pytest
from unittest.mock import patch, MagicMock
from src.sources.rss_generic import get_rss_events
from src.models import EventSource
from datetime import datetime

@pytest.fixture
def mock_feedparser():
    mock_entry = MagicMock()
    mock_entry.title = "RSS Event Title"
    mock_entry.summary = "RSS event summary."
    mock_entry.published = "Wed, 27 Mar 2024 18:00:00 GMT"
    mock_entry.link = "https://mtlblog.com/event/123"
    mock_entry.get.side_effect = lambda k, d=None: d if k != 'id' else "rss-123"
    mock_feed = MagicMock()
    mock_feed.entries = [mock_entry]
    with patch("feedparser.parse", return_value=mock_feed):
        yield

def test_get_rss_events(mock_feedparser):
    events = get_rss_events()
    assert len(events) == 2  # One for each feed in RSS_FEEDS
    for event in events:
        assert event.title == "RSS Event Title"
        assert event.source in (EventSource.MTL_BLOG, EventSource.GAZETTE)
        assert event.source_id == "rss-123"
        assert event.url == "https://mtlblog.com/event/123" 