from typing import List
import os
from datetime import datetime, timedelta
import requests
from ..models import Event, EventSource

TICKETMASTER_API_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

def get_ticketmaster_events() -> List[Event]:
    """
    Fetch events from Ticketmaster API for Montreal.
    Returns a list of Event objects.
    """
    TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
    if not TICKETMASTER_API_KEY:
        raise ValueError("TICKETMASTER_API_KEY environment variable not set")

    # Date range: next 30 days
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)

    params = {
        "apikey": TICKETMASTER_API_KEY,
        "city": "Montreal",
        "countryCode": "CA",
        "startDateTime": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endDateTime": end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "size": 100,
        "sort": "date,asc",
    }

    response = requests.get(TICKETMASTER_API_URL, params=params)
    response.raise_for_status()
    data = response.json()
    events = []
    for event_data in data.get("_embedded", {}).get("events", []):
        try:
            start_dt = datetime.fromisoformat(event_data["dates"]["start"]["dateTime"].replace("Z", "+00:00"))
            if start_dt < datetime.now():
                continue
            end_dt = start_dt
            if "end" in event_data["dates"] and event_data["dates"]["end"].get("dateTime"):
                end_dt = datetime.fromisoformat(event_data["dates"]["end"]["dateTime"].replace("Z", "+00:00"))
            elif event_data["dates"]["start"].get("dateTBD"):
                # If time is TBD, treat as all-day
                end_dt = start_dt + timedelta(hours=23, minutes=59)
            venue = event_data.get("_embedded", {}).get("venues", [{}])[0]
            event = Event(
                title=event_data["name"],
                description=event_data.get("info", ""),
                start_dt=start_dt,
                end_dt=end_dt,
                location=venue.get("name", "TBD"),
                url=event_data["url"],
                source=EventSource.TICKETMASTER,
                source_id=event_data["id"],
                is_all_day=event_data["dates"]["start"].get("dateTBD", False),
                popularity=None  # Ticketmaster does not provide popularity
            )
            events.append(event)
        except (KeyError, ValueError) as e:
            print(f"Error parsing Ticketmaster event {event_data.get('id', 'unknown')}: {e}")
            continue
    return events 