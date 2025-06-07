from typing import List
import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from .models import Event

SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')

def get_calendar_service():
    """Initialize and return Google Calendar service."""
    credentials = service_account.Credentials.from_service_account_info(
        info=eval(os.getenv('GOOGLE_APPLICATION_CREDENTIALS')),
        scopes=SCOPES
    )
    return build('calendar', 'v3', credentials=credentials)

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
    
    # Get existing events
    existing_events = {}
    page_token = None
    while True:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            pageToken=page_token,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        for event in events_result.get('items', []):
            source_id = event.get('extendedProperties', {}).get('private', {}).get('source_id')
            if source_id:
                existing_events[source_id] = event['id']
                
        page_token = events_result.get('nextPageToken')
        if not page_token:
            break
    
    # Sync events
    for event in events:
        calendar_event = event_to_calendar_event(event)
        
        if event.source_id in existing_events:
            # Update existing event
            service.events().update(
                calendarId=CALENDAR_ID,
                eventId=existing_events[event.source_id],
                body=calendar_event
            ).execute()
        else:
            # Create new event
            service.events().insert(
                calendarId=CALENDAR_ID,
                body=calendar_event
            ).execute() 