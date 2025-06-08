from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class EventSource(Enum):
    TOURISME_MTL = "tourisme_mtl"
    EVENTBRITE = "eventbrite"
    TICKETMASTER = "ticketmaster"
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