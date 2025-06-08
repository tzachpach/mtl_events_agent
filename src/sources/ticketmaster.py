from typing import List, Optional
import os, datetime, requests
from ..models import Event, EventSource
from ..utils.http import get_json

API_KEY = os.getenv("TICKETMASTER_API_KEY")  # ← match workflow secret
BASE = "https://app.ticketmaster.com/discovery/v2/events.json"

def get_ticketmaster_events() -> List[Event]:
    if not API_KEY:          # no key => safe no-op
        return []
    today = datetime.date.today()
    params = {
        "apikey": API_KEY,
        "city": "Montreal",
        "countryCode": "CA",
        "startDateTime": today.isoformat() + "T00:00:00Z",
        "endDateTime": (today + datetime.timedelta(days=35)).isoformat() + "T23:59:59Z",
        "size": "200",
        "sort": "date,asc",
    }
    data = get_json(BASE, params=params)
    events = data.get("_embedded", {}).get("events", [])
    out: List[Event] = []
    for ev in events:
        start = ev["dates"]["start"].get("dateTime") or ev["dates"]["start"]["localDate"]
        end   = ev["dates"]["end"].get("dateTime")   if ev["dates"].get("end") else None
        out.append(Event(
            title       = ev["name"],
            description = ev.get("info") or "",
            url         = ev.get("url"),
            start_dt    = Event.parse_datetime(start),
            end_dt      = Event.parse_datetime(end) if end else None,
            location    = ev.get("_embedded", {}).get("venues", [{}])[0].get("name"),
            popularity  = float(ev.get("promoter", {}).get("id", 0)) / 100,  # weak proxy
            source      = EventSource.TICKETMASTER,
            source_id   = ev["id"],
            is_all_day  = False,
        ))
    return out 