from typing import List, Dict
from datetime import datetime
import yaml
from pathlib import Path
from .models import Event, EventSource

DEFAULT_KEYWORDS = {
    "music": 1.0,
    "concert": 1.0,
    "food": 0.9,
    "improv": 0.8,
    "theatre": 0.8,
}

MAX_PER_DAY = 5
MAX_PARALLEL = 3

# Source priority weights
SOURCE_WEIGHTS = {
    EventSource.MTL_BLOG: 1.0,    # Highest priority
    EventSource.REDDIT: 0.8,      # Second priority
    EventSource.VILLE_MTL: 0.6,   # Third priority
    EventSource.TOURISME_MTL: 0.6,
    EventSource.EVENTBRITE: 0.6,
    EventSource.GAZETTE: 0.6,
}

def load_keywords() -> Dict[str, float]:
    """Load keywords from YAML file or return defaults."""
    try:
        with open(Path(__file__).parent / "keywords.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return DEFAULT_KEYWORDS

def score_event(event: Event, kw_map: Dict[str, float]) -> float:
    """Calculate a comprehensive score for an event.
    Score is based on source priority, keyword matches, and popularity.
    """
    # Source priority component (0.0 to 1.0)
    source_weight = SOURCE_WEIGHTS.get(event.source, 0.5)

    # Keyword score (0.0 to 1.0)
    def kw_match_score(text: str) -> float:
        # Look for keywords in both title and description
        matches = [kw_map[k] for k in kw_map if k.lower() in text.lower()]
        return max(matches) if matches else 0.0

    # Check both title and description for keywords
    keyword_score = max(
        kw_match_score(event.title),
        kw_match_score(event.description)
    )

    # Popularity component (if available, otherwise 0)
    popularity_component = event.popularity or 0.0

    # Duration component (slight boost for longer events)
    duration_component = 0.0
    if event.duration_hours > 4:
        duration_component = 0.1
    if event.is_all_day:
        duration_component += 0.15

    # Combine components with new weights:
    # - 40% source priority
    # - 30% keywords
    # - 20% popularity
    # - 10% duration
    score = (
        (0.4 * source_weight) +
        (0.3 * keyword_score) +
        (0.2 * popularity_component) +
        (0.1 * duration_component)
    )
    
    return score

def rank_and_filter(events: List[Event], kw_map: Dict[str, float] = None) -> List[Event]:
    """
    Rank and filter events based on source priority, keywords, popularity, and scheduling constraints.
    
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