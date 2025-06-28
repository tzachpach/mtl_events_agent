from typing import List, Tuple, Dict
from datetime import datetime, timedelta
import hashlib
import concurrent.futures
from .models import Event
from .ranker import rank_and_filter
from .sources import (
    # get_eventbrite_events,  # Eventbrite disabled
    # get_ticketmaster_events, # Removed as requested
    # get_tourisme_events,
    get_rss_events,
    get_reddit_events,
    get_city_events
)

def hash_title(title: str, date: datetime) -> str:
    """Create a unique hash for an event based on its title and date."""
    # Normalize title: lowercase, remove special chars
    normalized = ''.join(c.lower() for c in title if c.isalnum() or c.isspace())
    # Use date in YYYY-MM-DD format
    date_str = date.strftime('%Y-%m-%d')
    # Create hash
    return hashlib.md5(f"{normalized}|{date_str}".encode()).hexdigest()

def deduplicate(events: List[Event]) -> List[Event]:
    """Remove duplicate events based on title and date."""
    seen = set()
    unique = []
    
    for event in events:
        # Create hash from title and start date
        event_hash = hash_title(event.title, event.start_dt)
        
        if event_hash not in seen:
            seen.add(event_hash)
            unique.append(event)
            
    return unique

def pull_all() -> List[Event]:
    """Fetch events from all sources with timeouts."""
    all_events = []
    
    # Fetch from each source
    sources = [
        # get_eventbrite_events,
        # get_ticketmaster_events, # Removed as requested
        # get_tourisme_events,
        get_rss_events,
        get_reddit_events,
        get_city_events
    ]
    
    # Use a single ThreadPoolExecutor with a timeout for all sources
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(sources)) as executor:
        # Submit all source fetches with timeout
        futures = []
        for source in sources:
            future = executor.submit(source)
            futures.append((future, source.__name__))
        
        # Wait for all futures with timeout
        try:
            # Give each source appropriate timeout
            for future, source_name in futures:
                try:
                    # City events need more time for translations
                    timeout = 60 if source_name == 'get_city_events' else 30
                    events = future.result(timeout=timeout)
                    all_events.extend(events)
                    print(f"Fetched {len(events)} events from {source_name}")
                except concurrent.futures.TimeoutError:
                    print(f"Timeout fetching from {source_name}")
                    future.cancel()
                except Exception as e:
                    print(f"Error fetching from {source_name}: {e}")
                    future.cancel()
                    
        except Exception as e:
            print(f"Error during event fetching: {e}")
            # Cancel any remaining futures
            for future, _ in futures:
                future.cancel()
    
    return all_events

def process(events: List[Event]) -> Tuple[List[Event], List[Event]]:
    """
    Process events: deduplicate, separate festivals, and rank curated events.
    
    Returns:
        Tuple of (festivals, curated_events)
    """
    # Remove duplicates
    unique_events = deduplicate(events)
    
    # Separate festivals (multi-day events)
    festivals = []
    curated = []
    
    for event in unique_events:
        if event.is_all_day:
            festivals.append(event)
        else:
            curated.append(event)
    
    # Rank and filter curated events
    ranked_curated = rank_and_filter(curated)
    
    # Apply absolute hard cap
    ranked_curated = ranked_curated[:300]
    
    return festivals, ranked_curated 