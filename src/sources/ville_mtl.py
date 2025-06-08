from typing import List, Optional, Dict
from datetime import datetime, timedelta, date
import unicodedata
from ..models import Event, EventSource
from ..utils.http import fetch_csv

VILLE_MTL_EVENTS_CSV_URL = "https://donnees.montreal.ca/dataset/evenements-publics/resource/6decf611-6f11-4f34-bb36-324d804c9bad/download/evenements.csv"

def fix_encoding(text: str) -> str:
    if not isinstance(text, str):
        return text
    # Try to fix common encoding issues
    try:
        # Encode as latin1, decode as utf-8, then normalize
        fixed = text.encode('latin1').decode('utf-8')
        return unicodedata.normalize('NFC', fixed)
    except Exception:
        return text

def parse_datetime(dt_str: str, default: Optional[datetime] = None) -> Optional[datetime]:
    """Safely parse datetime string with error handling. This function is retained for general use if other sources need it, but Ville_MTL will use Event.parse_date for simpler parsing.
    """
    if not dt_str:
        return default
    try:
        return datetime.fromisoformat(dt_str)
    except (ValueError, TypeError):
        return default

def get_city_events() -> List[Event]:
    """
    Fetch events from Ville de Montréal open data CSV using fetch_csv helper.
    Returns a list of Event objects.
    """
    events = []
    try:
        # Use the new fetch_csv helper
        rows = fetch_csv(VILLE_MTL_EVENTS_CSV_URL)          # 10-s timeout, 5 MB max
        today = date.today()
        horizon = today + timedelta(days=35)
        out: List[Event] = []

        for r in rows:
            try:
                # Basic validation for required fields
                if not r.get("titre") or not r.get("url_fiche"): # url_fiche is source_id
                    continue

                start_dt = Event.parse_date(r["date_debut"])
                if not (today <= start_dt.date() <= horizon):             # skip far dates
                    continue

                end_dt_str = r.get("date_fin")
                end_dt = Event.parse_date(end_dt_str) if end_dt_str else start_dt + timedelta(hours=2)

                # Use fix_encoding for title and description
                title = fix_encoding(r["titre"])
                description = fix_encoding(r["description"])

                # Location handling as per prompt
                location = r.get("titre_adresse") or r.get("arrondissement")
                if not location:
                    location = "Montreal" # Default if both are missing

                event = Event(
                    title       = title,
                    description = description,
                    url         = r["url_fiche"],
                    start_dt    = start_dt,
                    end_dt      = end_dt,
                    location    = location,
                    popularity  = 0.2, # Default popularity as per prompt
                    source      = EventSource.VILLE_MTL,
                    source_id   = r["url_fiche"],
                    is_all_day  = False, # Default as per prompt
                )
                out.append(event)
            except (ValueError, KeyError, TypeError) as e:
                print(f"Error parsing Ville de Montréal event row: {r} - {e}")
                continue
    except Exception as e:
        print(f"Error fetching or processing Ville de Montréal CSV: {e}")
        
    return out 