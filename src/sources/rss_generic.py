from typing import List
from datetime import datetime, timedelta
import feedparser
import ssl
import urllib.request
from ..models import Event, EventSource

# Create a custom SSL context that doesn't verify certificates
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

RSS_FEEDS = [
    ("https://montreal.citynews.ca/feed", EventSource.MTL_BLOG),
    ("https://www.mtlblog.com/feeds/news.rss", EventSource.MTL_BLOG),
]

def get_rss_events() -> List[Event]:
    """
    Fetch events from configured RSS feeds.
    Returns a list of Event objects.
    """
    events = []
    for url, source in RSS_FEEDS:
        print(f"Fetching RSS feed from {url}")
        try:
            # Set a 10-second timeout for each feed
            response = urllib.request.urlopen(url, timeout=10)
            feed = feedparser.parse(response)
            print(f"Got {len(feed.entries)} entries from {url}")
            print(f"Feed status: {feed.status if hasattr(feed, 'status') else 'unknown'}")
            print(f"Feed headers: {feed.headers if hasattr(feed, 'headers') else 'unknown'}")
            print(f"Feed bozo: {feed.bozo if hasattr(feed, 'bozo') else 'unknown'}")
            if hasattr(feed, 'bozo_exception'):
                print(f"Feed exception: {feed.bozo_exception}")
            for entry in feed.entries:
                try:
                    # Use Event.parse_date for robust parsing and timezone awareness
                    dt_str = getattr(entry, 'published', getattr(entry, 'updated', ''))
                    if not dt_str:
                        print(f"No date found for entry: {entry.title}")
                        continue
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
        except Exception as e:
            print(f"Error fetching RSS feed from {url}: {e}")
            continue
    print(f"Total RSS events found: {len(events)}")
    return events 