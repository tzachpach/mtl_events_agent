from typing import List
from datetime import datetime, timedelta
import feedparser
from ..models import Event, EventSource

RSS_FEEDS = [
    ("https://www.mtlblog.com/rss", EventSource.MTL_BLOG),
    ("https://montrealgazette.com/feed/", EventSource.GAZETTE),
]

def parse_rss_datetime(dt_str: str) -> datetime:
    # Try to parse RFC822/ISO8601
    try:
        return datetime(*feedparser._parse_date(dt_str)[:6])
    except Exception:
        return datetime.now()

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
                start_dt = parse_rss_datetime(getattr(entry, 'published', getattr(entry, 'updated', '')))
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