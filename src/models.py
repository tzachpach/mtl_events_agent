from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum
import pytz
from email.utils import parsedate_to_datetime

# Montreal timezone
MONTREAL_TZ = pytz.timezone('America/Montreal')

class EventSource(Enum):
    TOURISME_MTL = "tourisme_mtl"
    EVENTBRITE = "eventbrite"
    MTL_BLOG = "mtl_blog"
    GAZETTE = "gazette"
    REDDIT = "reddit"
    VILLE_MTL = "ville_mtl"

@dataclass
class Event:
    """Represents a single event with all its metadata."""
    title: str
    description: str
    start_dt: datetime
    end_dt: datetime
    location: str
    url: str
    source: EventSource
    source_id: str
    is_all_day: bool = False
    popularity: Optional[float] = None
    score: Optional[float] = None
    
    def __post_init__(self):
        if self.end_dt < self.start_dt:
            raise ValueError("End time must be after start time")
        
    @property
    def duration_hours(self) -> float:
        """Returns the duration in hours."""
        return (self.end_dt - self.start_dt).total_seconds() / 3600
        
    @staticmethod
    def parse_date(dt_str: str) -> datetime:
        """Parses a date string into a timezone-aware datetime object for Montreal.
        Handles various ISO 8601-like formats and ensures timezone awareness.
        """
        if not dt_str:
            raise ValueError("Date string cannot be empty")
        
        # Try parsing as RFC 2822 format (used by RSS feeds)
        try:
            dt = parsedate_to_datetime(dt_str)
            return dt.astimezone(MONTREAL_TZ)
        except (ValueError, TypeError):
            pass
            
        # Try parsing as datetime with potential timezone info
        try:
            dt = datetime.fromisoformat(dt_str)
            if dt.tzinfo is None: # If no timezone info, assume Montreal time
                return MONTREAL_TZ.localize(dt)
            else:
                return dt.astimezone(MONTREAL_TZ)
        except ValueError:
            pass # Try other formats
            
        # Try parsing as date only (YYYY-MM-DD), then localize to Montreal and set time to midnight
        try:
            dt = datetime.strptime(dt_str, '%Y-%m-%d')
            return MONTREAL_TZ.localize(dt) # Midnight in Montreal timezone
        except ValueError:
            pass

        # Try parsing with a common combined format (e.g., from CSV like 'YYYY-MM-DD HH:MM:SS')
        try:
            dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            return MONTREAL_TZ.localize(dt)
        except ValueError:
            pass

        # If all parsing attempts fail
        raise ValueError(f"Could not parse date string: {dt_str}") 