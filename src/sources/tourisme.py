from typing import List
from datetime import datetime, timedelta
import requests
from ..models import Event, EventSource

TOURISME_API_URL = "https://www.mtl.org/en/api/whats-on"


def get_tourisme_events() -> List[Event]:
    """
    Fetch events from Tourisme Montréal JSON API.
    Returns a list of Event objects.
    """
    # Date range: next 30 days
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)

    params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "lang": "en",
        "limit": 100,
    }

    response = requests.get(TOURISME_API_URL, params=params)
    response.raise_for_status()
    data = response.json()
    events = []
    for event_data in data.get("data", []):
        try:
            start_dt = datetime.fromisoformat(event_data["start_date"])
            end_dt = datetime.fromisoformat(event_data["end_date"])
            if end_dt < datetime.now():
                continue
            event = Event(
                title=event_data["title"],
                description=event_data.get("description", ""),
                start_dt=start_dt,
                end_dt=end_dt,
                location=event_data.get("location", "Montreal"),
                url=event_data.get("url", ""),
                source=EventSource.TOURISME_MTL,
                source_id=str(event_data.get("id", "")),
                is_all_day=True if (end_dt - start_dt).days >= 1 else False,
                popularity=None
            )
            events.append(event)
        except (KeyError, ValueError) as e:
            print(f"Error parsing Tourisme Montréal event {event_data.get('id', 'unknown')}: {e}")
            continue
    return events 