from typing import List
import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from .models import Event
import time
import pytz


SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = os.getenv("GCAL_ID") or os.getenv("GOOGLE_CALENDAR_ID")
if not CALENDAR_ID:
    raise RuntimeError("GCAL_ID (or GOOGLE_CALENDAR_ID) var not set")

BATCH_SIZE = 50  # Process events in batches of 50

def get_calendar_service():
    sa_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not sa_path or not os.path.isfile(sa_path):
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS env var missing or file not found")
    creds = service_account.Credentials.from_service_account_file(sa_path, scopes=SCOPES)
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def list_events(start_date: datetime, end_date: datetime) -> List[dict]:
    """List events in the calendar between start_date and end_date."""
    service = get_calendar_service()
    
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start_date.isoformat() + 'Z',
        timeMax=end_date.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    return events_result.get('items', [])


def event_to_calendar_event(event: Event) -> dict:
    """Convert our Event model to Google Calendar event format."""
    calendar_event = {
        'summary': event.title,
        'description': f"{event.description}\n\nSource: {event.source.value}\nURL: {event.url}",
        'location': event.location,
        'start': {
            'dateTime' if not event.is_all_day else 'date': 
                event.start_dt.astimezone(pytz.utc).isoformat() if not event.is_all_day else event.start_dt.date().isoformat()
        },
        'end': {
            'dateTime' if not event.is_all_day else 'date': 
                event.end_dt.astimezone(pytz.utc).isoformat() if not event.is_all_day else event.end_dt.date().isoformat()
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
    
    # Calculate date range (only fetch next 35 days)
    now = datetime.utcnow()
    future = now + timedelta(days=35)  # Reduced from 365 to 35 days
    
    # Get existing events within date range
    existing_events = {}
    page_token = None
    
    # First, build a map of event dates to optimize calendar fetching
    event_dates = set()
    for event in events:
        event_dates.add(event.start_dt.date())
        if event.end_dt.date() != event.start_dt.date():
            event_dates.add(event.end_dt.date())
    
    print(f"\nFetching existing calendar events for {len(event_dates)} unique dates...")
    updated_count = 0
    created_count = 0
    error_count = 0
    
    # Only fetch calendar events for dates where we have events to sync
    for date in event_dates:
        date_start = datetime.combine(date, datetime.min.time())
        date_end = datetime.combine(date, datetime.max.time())
        
        try:
            events_result = service.events().list(
                calendarId=CALENDAR_ID,
                singleEvents=True,
                orderBy='startTime',
                timeMin=date_start.isoformat() + 'Z',
                timeMax=date_end.isoformat() + 'Z',
                maxResults=2500
            ).execute()
            
            for event in events_result.get('items', []):
                source_id = event.get('extendedProperties', {}).get('private', {}).get('source_id')
                if source_id:
                    existing_events[source_id] = event['id']
                    
        except Exception as e:
            print(f"Error fetching calendar events for {date}: {e}")
            error_count += 1
            continue
    
    print(f"Found {len(existing_events)} existing events in calendar")
    
    # Process events in smaller batches
    for i in range(0, len(events), BATCH_SIZE):
        batch = service.new_batch_http_request()
        batch_events = events[i:i + BATCH_SIZE]
        
        for event in batch_events:
            calendar_event = event_to_calendar_event(event)
            
            if event.source_id in existing_events:
                # Update existing event
                batch.add(service.events().update(
                    calendarId=CALENDAR_ID,
                    eventId=existing_events[event.source_id],
                    body=calendar_event
                ))
                updated_count += 1
            else:
                # Create new event
                batch.add(service.events().insert(
                    calendarId=CALENDAR_ID,
                    body=calendar_event
                ))
                created_count += 1
        
        # Execute batch operations
        try:
            batch.execute()
            time.sleep(0.1)  # Small delay between batches
        except Exception as e:
            print(f"Error syncing batch of events to calendar: {e}")
            error_count += 1
            continue  # Continue with next batch even if this one fails
            
    print(f"\nCalendar sync complete:")
    print(f"- Updated: {updated_count} events")
    print(f"- Created: {created_count} events")
    if error_count > 0:
        print(f"- Errors: {error_count}") 