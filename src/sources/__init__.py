"""
Event source modules for fetching events from various platforms.
"""

from typing import List
# from .eventbrite import get_eventbrite_events  # Disabled for now
from .reddit import get_reddit_events
from .rss_generic import get_rss_events
from .ville_mtl import get_city_events
# from .ticketmaster import get_ticketmaster_events # Removed as requested
from ..models import Event

__all__ = [
    # 'get_eventbrite_events',  # Disabled for now
    'get_reddit_events',
    'get_rss_events',
    'get_city_events',
    # 'get_ticketmaster_events', # Removed as requested
]

def get_all_events() -> List[Event]:
    """Fetch events from all available sources."""
    events = []
    # events.extend(get_eventbrite_events())  # Disabled for now
    events.extend(get_reddit_events())
    events.extend(get_rss_events())
    events.extend(get_city_events())
    # events.extend(get_ticketmaster_events())  # Removed as requested
    return events 