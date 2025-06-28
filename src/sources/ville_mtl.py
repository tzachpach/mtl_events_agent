from typing import List, Optional, Tuple, Dict
from datetime import datetime, timedelta, date
import unicodedata
import re
from ..models import Event, EventSource
from ..utils.http import fetch_csv
import requests
import os
import time

URL = (
    "https://donnees.montreal.ca/dataset/evenements-publics/"
    "resource/6decf611-6f11-4f34-bb36-324d804c9bad/download/evenements.csv"
)

# Cache for translations to avoid duplicate API calls
translation_cache: Dict[str, str] = {}

def translate_batch(texts: List[str], target_lang: str = 'en') -> List[str]:
    """
    Translate a batch of texts using Google Cloud Translation API.
    Returns list of translated texts, falling back to original if translation fails.
    """
    if not texts:
        return []
        
    # Filter out already cached translations
    to_translate = []
    text_to_idx = {}
    results = [""] * len(texts)
    
    for i, text in enumerate(texts):
        if text in translation_cache:
            results[i] = translation_cache[text]
        else:
            to_translate.append(text)
            text_to_idx[text] = i
    
    if not to_translate:
        return results
        
    try:
        url = "https://translation.googleapis.com/language/translate/v2"
        params = {
            'q': to_translate,
            'target': target_lang,
            'source': 'fr',
            'key': os.getenv('GOOGLE_TRANSLATE_KEY')
        }
        response = requests.post(url, params=params)
        if response.status_code == 200:
            translations = response.json()['data']['translations']
            for text, trans in zip(to_translate, translations):
                translated = trans['translatedText']
                translation_cache[text] = translated
                results[text_to_idx[text]] = translated
    except Exception as e:
        print(f"Batch translation error: {e}")
        # Fall back to original texts
        for text in to_translate:
            results[text_to_idx[text]] = text
            
    return results

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
        print("\nFetching city events:")
        fetch_start = time.time()
        rows = fetch_csv(URL)          # 12-s timeout, 5 MB cap
        print(f"[{time.time() - fetch_start:.1f}s] CSV fetched")
        
        today = date.today()
        horizon = today + timedelta(days=35)
        
        # Prepare batches for translation
        titles_fr = []
        descriptions_fr = []
        valid_rows = []
        
        # First pass: collect texts for translation
        parse_start = time.time()
        for r in rows:
            try:
                start = Event.parse_date(r["date_debut"])
                if not (today <= start.date() <= horizon):
                    continue
                    
                title_fr = fix_encoding(r["titre"])
                description_fr = fix_encoding(r["description"])
                
                titles_fr.append(title_fr)
                descriptions_fr.append(description_fr)
                valid_rows.append((r, start))
            except (ValueError, KeyError, TypeError) as e:
                print(f"Error parsing Ville de Montréal event row: {r} - {e}")
                continue
        print(f"[{time.time() - parse_start:.1f}s] Parsed {len(valid_rows)} valid events")
                
        # Batch translate all texts
        trans_start = time.time()
        titles_en = translate_batch(titles_fr)
        descriptions_en = translate_batch(descriptions_fr)
        print(f"[{time.time() - trans_start:.1f}s] Translated {len(titles_fr)} titles and {len(descriptions_fr)} descriptions")
        print(f"Translation cache hits: {len(translation_cache)}")
        
        # Second pass: create events with translations
        create_start = time.time()
        for i, (r, start) in enumerate(valid_rows):
            try:
                title_fr = titles_fr[i]
                title_en = titles_en[i]
                description_fr = descriptions_fr[i]
                description_en = descriptions_en[i]
                
                # Combine French and English versions
                title = f"{title_fr} / {title_en}" if title_en != title_fr else title_fr
                description = f"🇫🇷 {description_fr}\n\n🇬🇧 {description_en}" if description_en != description_fr else description_fr
                
                start_dt, end_dt = parse_time_from_description(description_fr, start)
                
                events.append(
                    Event(
                        title       = title,
                        description = description,
                        url         = r["url_fiche"],
                        start_dt    = start_dt,
                        end_dt      = end_dt,
                        location    = fix_encoding(r.get("titre_adresse") or r.get("arrondissement") or "Montreal"),
                        popularity  = 0.2,
                        source      = EventSource.VILLE_MTL,
                        source_id   = r["url_fiche"],
                        is_all_day  = False,
                    )
                )
            except Exception as e:
                print(f"Error creating event from row: {e}")
                continue
        print(f"[{time.time() - create_start:.1f}s] Created {len(events)} events")
        print(f"Total time: {time.time() - fetch_start:.1f}s")
                
    except Exception as e:
        print(f"Error fetching or processing Ville de Montréal CSV: {e}")
    return events 