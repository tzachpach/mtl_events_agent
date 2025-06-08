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

def score_event(event: Event, kw_map: Dict[str, float]) -> float:
    """Calculate a comprehensive score for an event.
    Score is based on popularity, duration, and keyword matches.
    """
    # Keyword score
    def kw_match_score(title: str) -> float:
        return max((kw_map[k] for k in kw_map if k in title.lower()), default=0.0)

    keyword_score = kw_match_score(event.title)

    # Popularity component (if available, otherwise 0)
    popularity_component = event.popularity or 0.0

    # Duration component (longer events might get a slight boost, or specific ranges)
    # This is a simple example; adjust logic as needed.
    duration_component = 0.0
    if event.duration_hours > 4: # Example: give a small boost for longer events
        duration_component = 0.1
    if event.is_all_day: # Festivals or all-day events
        duration_component += 0.15

    # Combine components. Adjust weights as desired.
    # Example: 60% popularity, 20% keywords, 20% duration
    score = (0.6 * popularity_component) + (0.2 * keyword_score) + (0.2 * duration_component)
    
    return score

def rank_and_filter(events: List[Event], kw_map: Dict[str, float] = None) -> List[Event]:
    """
    Rank and filter events based on popularity, keywords, scheduling constraints, and minimum score.
    
    Args:
        events: List of events to rank and filter
        kw_map: Optional keyword to weight mapping. If None, loads from keywords.yaml
        
    Returns:
        Filtered list of events that meet the scheduling constraints and minimum score
    """
    if kw_map is None:
        kw_map = load_keywords()
        
    scored_events = []
    for e in events:
        e.score = score_event(e, kw_map)
        if e.score >= 0.2: # Filter out events below a certain score
            scored_events.append(e)

    # Group by day and apply scheduling constraints
    out = []
    by_day = {}
    
    # Sort by score (descending) and start time (ascending)
    for e in sorted(scored_events, key=lambda x: (-x.score, x.start_dt)):
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