from typing import List
from datetime import datetime, timedelta
import requests
from ..models import Event, EventSource

REDDIT_API_URL = "https://www.reddit.com/r/montreal/search.json"
USER_AGENT = "mtl-events-agent/0.1 by u/yourusername"


def get_reddit_events() -> List[Event]:
    """
    Fetch events from the r/montreal "What's on this week" thread.
    Returns a list of Event objects.
    """
    params = {
        "q": "What's on this week",
        "restrict_sr": 1,
        "sort": "new",
        "limit": 1
    }
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(REDDIT_API_URL, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    events = []
    posts = data.get("data", {}).get("children", [])
    if not posts:
        return events
    thread = posts[0]["data"]
    # Parse the thread body for event lines (very basic: one event per line)
    body = thread.get("selftext", "")
    for line in body.splitlines():
        if not line.strip() or '|' not in line:
            continue
        # Try to parse: "Mar 28 | Event Title | Location | URL"
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 2:
            continue
        try:
            # Parse date (assume current year)
            date_str = parts[0]
            try:
                event_date = datetime.strptime(date_str + f" {datetime.now().year}", "%b %d %Y")
            except Exception:
                event_date = datetime.now()
            title = parts[1]
            location = parts[2] if len(parts) > 2 else "Montreal"
            url = parts[3] if len(parts) > 3 else thread.get("url", "")
            event = Event(
                title=title,
                description="Reddit r/montreal community event.",
                start_dt=event_date,
                end_dt=event_date + timedelta(hours=2),
                location=location,
                url=url,
                source=EventSource.REDDIT,
                source_id=thread["id"] + title,
                is_all_day=False,
                popularity=None
            )
            events.append(event)
        except Exception as e:
            print(f"Error parsing Reddit event line: {e}")
            continue
    return events 