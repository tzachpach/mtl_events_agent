from typing import List
import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from .models import Event


SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = (
    os.getenv("GCAL_ID")              # preferred
    or os.getenv("GOOGLE_CALENDAR_ID")  # backward compat
)
if not CALENDAR_ID:
    raise RuntimeError("GCAL_ID (or GOOGLE_CALENDAR_ID) env var not set")

def get_calendar_service():
    sa_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not sa_path or not os.path.isfile(sa_path):
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS env var missing or file not found")
    creds = service_account.Credentials.from_service_account_file(sa_path, scopes=SCOPES)
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def event_to_calendar_event(event: Event) -> dict:
    """Convert our Event model to Google Calendar event format."""
    calendar_event = {
        'summary': event.title,
        'description': f"{event.description}\n\nSource: {event.source.value}\nURL: {event.url}",
        'location': event.location,
        'start': {
            'dateTime' if not event.is_all_day else 'date': 
                event.start_dt.isoformat() if not event.is_all_day else event.start_dt.date().isoformat()
        },
        'end': {
            'dateTime' if not event.is_all_day else 'date': 
                event.end_dt.isoformat() if not event.is_all_day else event.end_dt.date().isoformat()
        },
        'extendedProperties': {
            'private': {
                'source': event.source.value,
                'source_id': event.source_id
            }
        }
    }
    return calendar_event

def sync(events: List[Event]) -> None:
    """
    Sync events to Google Calendar.
    Creates new events and updates existing ones based on source_id.
    """
    if not CALENDAR_ID:
        raise ValueError("GOOGLE_CALENDAR_ID environment variable not set")
        
    service = get_calendar_service()
    
    # Calculate date range (now to 35 days from now)
    now = datetime.utcnow()
    future = now + timedelta(days=35)
    
    # Get existing events within date range
    existing_events = {}
    page_token = None
    while True:
        try:
            events_result = service.events().list(
                calendarId=CALENDAR_ID,
                pageToken=page_token,
                singleEvents=True,
                orderBy='startTime',
                timeMin=now.isoformat() + 'Z',
                timeMax=future.isoformat() + 'Z',
                maxResults=2500  # Limit results per page
            ).execute()
            
            for event in events_result.get('items', []):
                source_id = event.get('extendedProperties', {}).get('private', {}).get('source_id')
                if source_id:
                    existing_events[source_id] = event['id']
                    
            page_token = events_result.get('nextPageToken')
            if not page_token:
                break
                
        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            break
    
    # Prepare batch operations
    batch = service.new_batch_http_request()
    
    # Sync events
    for event in events:
        calendar_event = event_to_calendar_event(event)
        
        if event.source_id in existing_events:
            # Update existing event
            batch.add(service.events().update(
                calendarId=CALENDAR_ID,
                eventId=existing_events[event.source_id],
                body=calendar_event
            ))
        else:
            # Create new event
            batch.add(service.events().insert(
                calendarId=CALENDAR_ID,
                body=calendar_event
            ))
    
    # Execute batch operations
    try:
        batch.execute()
    except Exception as e:
        print(f"Error syncing events to calendar: {e}")
        raise 