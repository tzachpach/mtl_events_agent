from typing import List, Optional
from datetime import datetime, timedelta
import requests
import os
from ..models import Event, EventSource

PUBLIC_REDDIT_JSON_URL = "https://www.reddit.com/r/montreal/.json?limit=50"
USER_AGENT = "mtl-events-agent/0.1 (by tzachlarboni for personal project)"

def get_reddit_events() -> List[Event]:
    """
    Fetch events from Reddit's r/montreal subreddit.
    Falls back to public JSON feed if REDDIT_CLIENT_ID/SECRET are absent.
    Returns a list of Event objects.
    """
    events = []
    headers = {"User-Agent": USER_AGENT}
    keywords = ["festival", "event", "happening", "thing to do"]

    # Reddit API credentials are not directly used in this public fallback logic.
    # The presence of these vars would typically trigger a different (authenticated) flow.
    reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
    reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")

    try:
        response = requests.get(PUBLIC_REDDIT_JSON_URL, headers=headers, timeout=8)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        posts = data.get("data", {}).get("children", [])
        for post in posts:
            post_data = post.get("data", {})
            title = post_data.get("title", "")
            
            # Check if title contains any of the keywords (case-insensitive)
            if not any(keyword in title.lower() for keyword in keywords):
                continue  # Skip if no keyword found

            # Map fields into Event objects
            try:
                description = post_data.get("selftext", "").strip()
                if not description:
                    description = post_data.get("url", "").strip()  # Use URL as description if selftext is empty

                url = post_data.get("url", "")
                if not url:  # Basic validation for URL
                    continue

                start_dt = datetime.now()
                end_dt = start_dt + timedelta(hours=2)
                
                location = "Montreal"  # Default location as per prompt

                event = Event(
                    title=title,
                    description=description,
                    start_dt=start_dt,
                    end_dt=end_dt,
                    location=location,
                    url=url,
                    source=EventSource.REDDIT,
                    source_id=post_data.get("id", url),  # Use id, fallback to url
                    is_all_day=False,
                    popularity=0.1  # Small default popularity
                )
                events.append(event)
            except Exception as e:
                print(f"Error parsing Reddit post data: {e} - Post: {post_data.get('title', 'N/A')}")
                continue

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Reddit events: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while processing Reddit events: {e}")
        
    return events 