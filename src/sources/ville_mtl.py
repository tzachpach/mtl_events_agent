from typing import List
from datetime import datetime, timedelta, date
import unicodedata
from ..models import Event, EventSource
from ..utils.http import fetch_csv

URL = (
    "https://donnees.montreal.ca/dataset/evenements-publics/"
    "resource/6decf611-6f11-4f34-bb36-324d804c9bad/download/evenements.csv"
)

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

def get_city_events() -> List[Event]:
    events = []
    try:
        rows = fetch_csv(URL)          # 12-s timeout, 5 MB cap
        today = date.today()
        horizon = today + timedelta(days=35)
        out: List[Event] = []
        for r in rows:
            try:
                start = Event.parse_date(r["date_debut"])
                if not (today <= start.date() <= horizon):
                    continue
                out.append(
                    Event(
                        title       = fix_encoding(r["titre"]),
                        description = fix_encoding(r["description"]),
                        url         = r["url_fiche"],
                        start_dt    = start,
                        end_dt      = Event.parse_date(r["date_fin"]) if r["date_fin"] else start + timedelta(hours=2),
                        location    = fix_encoding(r.get("titre_adresse") or r.get("arrondissement") or "Montreal"), # Default to Montreal if both missing
                        popularity  = 0.2,
                        source      = EventSource.VILLE_MTL,
                        source_id   = r["url_fiche"],
                        is_all_day  = False,
                    )
                )
            except (ValueError, KeyError, TypeError) as e:
                print(f"Error parsing Ville de Montréal event row: {r} - {e}")
                continue
    except Exception as e:
        print(f"Error fetching or processing Ville de Montréal CSV: {e}")
    return out 