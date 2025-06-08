from typing import List
from datetime import datetime, timedelta
import feedparser
from ..models import Event, EventSource

RSS_FEEDS = [
    ("https://www.mtlblog.com/rss", EventSource.MTL_BLOG),
    ("https://montrealgazette.com/feed/", EventSource.GAZETTE),
]

def get_rss_events() -> List[Event]:
    """
    Fetch events from configured RSS feeds.
    Returns a list of Event objects.
    """
    events = []
    for url, source in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            try:
                # Use Event.parse_date for robust parsing and timezone awareness
                dt_str = getattr(entry, 'published', getattr(entry, 'updated', ''))
                start_dt = Event.parse_date(dt_str)
                # Assume 2-hour event if not all-day
                end_dt = start_dt + timedelta(hours=2)
                event = Event(
                    title=entry.title,
                    description=getattr(entry, 'summary', ''),
                    start_dt=start_dt,
                    end_dt=end_dt,
                    location="Montreal",
                    url=entry.link,
                    source=source,
                    source_id=entry.get('id', entry.link),
                    is_all_day=False,
                    popularity=None
                )
                events.append(event)
            except Exception as e:
                print(f"Error parsing RSS event from {url}: {e}")
                continue
    return events 