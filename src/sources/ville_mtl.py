from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd
import unicodedata
from ..models import Event, EventSource
from ..utils.http import get_csv

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
    """Safely parse datetime string with error handling."""
    if not dt_str or pd.isna(dt_str):
        return default
    try:
        return datetime.fromisoformat(dt_str)
    except (ValueError, TypeError):
        return default

def get_city_events() -> List[Event]:
    """
    Fetch events from Ville de Montréal open data CSV.
    Returns a list of Event objects.
    """
    events = []
    try:
        df = get_csv(VILLE_MTL_EVENTS_CSV_URL)
        
        # Filter for events within the next 35 days
        now = datetime.now()
        future_limit = now + timedelta(days=35)

        for _, row in df.iterrows():
            try:
                # Required fields with validation
                title = fix_encoding(str(row.get('titre', '')).strip())
                if not title:
                    continue

                description = fix_encoding(str(row.get('description', '')).strip())
                url = str(row.get('url_fiche', '')).strip()
                if not url:
                    continue

                # Parse dates with fallbacks
                start_dt = parse_datetime(row.get('date_debut'), now)
                end_dt = parse_datetime(row.get('date_fin'))
                
                if not start_dt:
                    continue
                
                if not end_dt:
                    end_dt = start_dt + timedelta(hours=2)

                # Handle duration for is_all_day
                duration = end_dt - start_dt
                is_all_day = duration.total_seconds() / 3600 >= 8  # More than 8 hours for all-day

                # Enhanced location handling
                location_titre_adresse = fix_encoding(str(row.get('titre_adresse', '')).strip())
                location_arrondissement = fix_encoding(str(row.get('arrondissement', 'Montreal')).strip())
                
                # Clean up location fields
                location_titre_adresse = '' if pd.isna(location_titre_adresse) else location_titre_adresse
                location_arrondissement = 'Montreal' if pd.isna(location_arrondissement) else location_arrondissement
                
                # Combine location fields if both exist
                location = f"{location_titre_adresse}, {location_arrondissement}" if location_titre_adresse else location_arrondissement

                # Additional metadata
                category = fix_encoding(str(row.get('categorie', '')).strip())
                if category:
                    description = f"Category: {category}\n\n{description}"

                # Filter events within the next 35 days and future events
                if end_dt < now or start_dt > future_limit:
                    continue

                # Calculate popularity based on category and duration
                base_popularity = 0.2
                if category.lower() in ['festival', 'concert', 'spectacle']:
                    base_popularity += 0.1
                if duration.total_seconds() / 3600 > 24:  # Multi-day events
                    base_popularity += 0.05

                event = Event(
                    title=title,
                    description=description,
                    start_dt=start_dt,
                    end_dt=end_dt,
                    location=location,
                    url=url,
                    source=EventSource.VILLE_MTL,
                    source_id=url,  # url_fiche is unique enough for source_id
                    is_all_day=is_all_day,
                    popularity=base_popularity
                )
                events.append(event)
            except (ValueError, KeyError) as e:
                print(f"Error parsing Ville de Montréal event row: {row.to_dict()} - {e}")
                continue
    except Exception as e:
        print(f"Error fetching or processing Ville de Montréal CSV: {e}")
    return events 