from typing import List, Optional, Tuple
from datetime import datetime, timedelta, date
import unicodedata
import re
from ..models import Event, EventSource
from ..utils.http import fetch_csv
import requests
import os

URL = (
    "https://donnees.montreal.ca/dataset/evenements-publics/"
    "resource/6decf611-6f11-4f34-bb36-324d804c9bad/download/evenements.csv"
)

def translate_text(text: str, target_lang: str = 'en') -> str:
    """
    Translate text using Google Cloud Translation API.
    Returns the original text if translation fails.
    """
    try:
        url = "https://translation.googleapis.com/language/translate/v2"
        params = {
            'q': text,
            'target': target_lang,
            'source': 'fr',
            'key': os.getenv('GOOGLE_TRANSLATE_KEY')
        }
        response = requests.post(url, params=params)
        if response.status_code == 200:
            return response.json()['data']['translations'][0]['translatedText']
    except Exception as e:
        print(f"Translation error: {e}")
    return text

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

def parse_time_from_description(description: str, start_date: datetime) -> Tuple[datetime, datetime]:
    """
    Parse time from description text like "Jeudi 3 juillet 2025 de 18 h 30 à 20 h 00"
    Returns a tuple of (start_datetime, end_datetime)
    """
    # Try to find time pattern like "18 h 30" or "20 h 00"
    time_pattern = r'(\d{1,2})\s*h\s*(\d{2})?'
    times = re.findall(time_pattern, description)
    
    if len(times) >= 2:  # We found both start and end times
        start_hour = int(times[0][0])
        start_min = int(times[0][1]) if times[0][1] else 0
        end_hour = int(times[1][0])
        end_min = int(times[1][1]) if times[1][1] else 0
        
        start_dt = start_date.replace(hour=start_hour, minute=start_min)
        end_dt = start_date.replace(hour=end_hour, minute=end_min)
        
        # If end time is earlier than start time, assume it's next day
        if end_dt < start_dt:
            end_dt = end_dt + timedelta(days=1)
            
        return start_dt, end_dt
    
    return start_date, start_date + timedelta(hours=2)  # Default to 2-hour duration

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
                    
                # Parse time from description if available
                description_fr = fix_encoding(r["description"])
                title_fr = fix_encoding(r["titre"])
                
                # Translate title and description to English
                title_en = translate_text(title_fr)
                description_en = translate_text(description_fr)
                
                # Combine French and English versions
                title = f"{title_fr} / {title_en}" if title_en != title_fr else title_fr
                description = f"🇫🇷 {description_fr}\n\n🇬🇧 {description_en}" if description_en != description_fr else description_fr
                
                start_dt, end_dt = parse_time_from_description(description_fr, start)
                
                out.append(
                    Event(
                        title       = title,
                        description = description,
                        url         = r["url_fiche"],
                        start_dt    = start_dt,
                        end_dt      = end_dt,
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