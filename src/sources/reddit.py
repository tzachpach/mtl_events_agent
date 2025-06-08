from typing import List, Optional
from datetime import datetime, timedelta
import requests
import os
import praw
from ..models import Event, EventSource

PUBLIC_REDDIT_JSON_URL = "https://www.reddit.com/r/montreal/.json?limit=50"
USER_AGENT_PUBLIC = "mtl-events-agent/0.1 (public fallback)"
USER_AGENT_PRAW = "mtl-events-agent/0.1 (PRAW client)"

def get_reddit_events() -> List[Event]:
    """
    Fetch events from Reddit's r/montreal subreddit.
    Uses PRAW if REDDIT_CLIENT_ID/SECRET are present, falls back to public JSON feed otherwise.
    Returns a list of Event objects.
    """
    events = []
    keywords = ["festival", "event", "happening", "thing to do"]

    reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
    reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")

    if reddit_client_id and reddit_client_secret:
        # Use PRAW if credentials are provided
        try:
            reddit = praw.Reddit(
                client_id=reddit_client_id,
                client_secret=reddit_client_secret,
                user_agent=USER_AGENT_PRAW,
            )
            # Fetch top posts (adjust logic if you need specific search)
            # For simplicity, let's fetch from the subreddit's hot posts for now
            # You might want to use reddit.subreddit("montreal").search() for specific queries
            for submission in reddit.subreddit("montreal").hot(limit=50):
                title = submission.title
                if not any(keyword in title.lower() for keyword in keywords):
                    continue

                description = submission.selftext or submission.url
                url = submission.url

                # PRAW submissions have a creation timestamp, use it for start_dt if possible
                created_utc = datetime.fromtimestamp(submission.created_utc)
                start_dt = created_utc
                end_dt = start_dt + timedelta(hours=2)
                
                location = "Montreal"

                event = Event(
                    title=title,
                    description=description,
                    start_dt=start_dt,
                    end_dt=end_dt,
                    location=location,
                    url=url,
                    source=EventSource.REDDIT,
                    source_id=submission.id,
                    is_all_day=False,
                    popularity=submission.score / 100.0 if submission.score else 0.05 # Proxy popularity
                )
                events.append(event)
        except Exception as e:
            print(f"Error fetching Reddit events with PRAW: {e}")
            # Fallback to public feed if PRAW fails
            return _fetch_public_reddit_events(keywords)
    else:
        # Fallback to public JSON feed
        return _fetch_public_reddit_events(keywords)
        
    return events

def _fetch_public_reddit_events(keywords: List[str]) -> List[Event]:
    """Helper to fetch events from the public Reddit JSON feed."""
    public_events = []
    headers = {"User-Agent": USER_AGENT_PUBLIC}
    try:
        response = requests.get(PUBLIC_REDDIT_JSON_URL, headers=headers, timeout=8)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        posts = data.get("data", {}).get("children", [])
        for post in posts:
            post_data = post.get("data", {})
            title = post_data.get("title", "")
            
            if not any(keyword in title.lower() for keyword in keywords):
                continue

            description = post_data.get("selftext", "").strip()
            if not description:
                description = post_data.get("url", "").strip()

            url = post_data.get("url", "")
            if not url:
                continue

            start_dt = datetime.now()
            end_dt = start_dt + timedelta(hours=2)
            location = "Montreal"

            event = Event(
                title=title,
                description=description,
                start_dt=start_dt,
                end_dt=end_dt,
                location=location,
                url=url,
                source=EventSource.REDDIT,
                source_id=post_data.get("id", url),
                is_all_day=False,
                popularity=0.1
            )
            public_events.append(event)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching public Reddit events: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while processing public Reddit events: {e}")
        
    return public_events 