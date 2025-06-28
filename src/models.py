from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum
import pytz
from email.utils import parsedate_to_datetime

# Montreal timezone
MONTREAL_TZ = pytz.timezone('America/Montreal')

class EventSource(Enum):
    VILLE_MTL = "ville_mtl"
    TOURISME_MTL = "tourisme_mtl"
    EVENTBRITE = "eventbrite"
    TICKETMASTER = "ticketmaster"
    REDDIT = "reddit"
    MTL_BLOG = "mtl_blog"
    GAZETTE = "gazette"

@dataclass
class Event:
    """Represents a single event with all its metadata."""
    title: str
    description: str
    url: str
    start_dt: datetime
    end_dt: datetime
    location: str
    popularity: float
    source: EventSource
    source_id: str
    is_all_day: bool = False
    score: float = None
    
    def __post_init__(self):
        """Ensure all datetimes are timezone-aware and in Montreal time."""
        montreal_tz = pytz.timezone('America/Montreal')
        
        # Handle start_dt
        if self.start_dt.tzinfo is None:
            self.start_dt = montreal_tz.localize(self.start_dt)
        else:
            self.start_dt = self.start_dt.astimezone(montreal_tz)
            
        # Handle end_dt
        if self.end_dt.tzinfo is None:
            self.end_dt = montreal_tz.localize(self.end_dt)
        else:
            self.end_dt = self.end_dt.astimezone(montreal_tz)
        
    @property
    def duration_hours(self) -> float:
        """Returns the duration in hours."""
        return (self.end_dt - self.start_dt).total_seconds() / 3600
        
    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """Parse date string and ensure timezone is set to Montreal."""
        montreal_tz = pytz.timezone('America/Montreal')
        
        # Try parsing as RFC 2822 format (used by RSS feeds)
        try:
            dt = parsedate_to_datetime(date_str)
            return dt.astimezone(montreal_tz)
        except (ValueError, TypeError):
            pass
            
        # Try parsing as ISO format
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=pytz.UTC)
            return dt.astimezone(montreal_tz)
        except ValueError:
            pass
            
        # Try common date formats
        formats = [
            '%Y-%m-%d',           # YYYY-MM-DD
            '%Y-%m-%d %H:%M:%S',  # YYYY-MM-DD HH:MM:SS
            '%d/%m/%Y %H:%M',     # DD/MM/YYYY HH:MM
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return montreal_tz.localize(dt)
            except ValueError:
                continue
                
        raise ValueError(f"Could not parse date string: {date_str}") 