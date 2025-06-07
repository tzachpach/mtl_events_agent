from typing import List, Dict
from datetime import datetime
import yaml
from pathlib import Path
from .models import Event

DEFAULT_KEYWORDS = {
    "improv": 1.0,
    "free": 0.8,
    "pay-what-you-can": 0.8,
    "spoken-word": 0.6,
    "trail": 0.4,
}

MAX_PER_DAY = 5
MAX_PARALLEL = 3

def load_keywords() -> Dict[str, float]:
    """Load keywords from YAML file or return defaults."""
    try:
        with open(Path(__file__).parent / "keywords.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return DEFAULT_KEYWORDS

def rank_and_filter(events: List[Event], kw_map: Dict[str, float] = None) -> List[Event]:
    """
    Rank and filter events based on popularity, keywords, and scheduling constraints.
    
    Args:
        events: List of events to rank and filter
        kw_map: Optional keyword to weight mapping. If None, loads from keywords.yaml
        
    Returns:
        Filtered list of events that meet the scheduling constraints
    """
    if kw_map is None:
        kw_map = load_keywords()
        
    def kw_score(title: str) -> float:
        """Calculate keyword score for a title."""
        return max((kw_map[k] for k in kw_map if k in title.lower()), default=0.0)

    # Calculate base scores
    for e in events:
        e.score = 0.6 * (e.popularity or 0) + 0.4 * kw_score(e.title)

    # Group by day and apply scheduling constraints
    out = []
    by_day = {}
    
    # Sort by score (descending) and start time (ascending)
    for e in sorted(events, key=lambda x: (-x.score, x.start_dt)):
        day = e.start_dt.date()
        by_day.setdefault(day, [])
        
        # Find overlapping events
        active = [pe for pe in by_day[day]
                 if not (e.end_dt <= pe.start_dt or e.start_dt >= pe.end_dt)]
        
        # Apply constraints
        if len(by_day[day]) < MAX_PER_DAY and len(active) < MAX_PARALLEL:
            by_day[day].append(e)
            out.append(e)
            
    return out 