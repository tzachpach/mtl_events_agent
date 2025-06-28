from datetime import datetime, timezone
from src.calendar_client import list_events

# Jazz Festival dates for 2025
start_date = datetime(2025, 6, 26, tzinfo=timezone.utc)
end_date = datetime(2025, 7, 5, tzinfo=timezone.utc)

print(f"\nChecking Jazz Festival events ({start_date.date()} to {end_date.date()}):")
print("-" * 80)

events = list_events(start_date, end_date)

jazz_events = [e for e in events if 'jazz' in e.get('summary', '').lower()]
print(f"\nFound {len(jazz_events)} jazz-related events:")

for event in jazz_events:
    start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', 'No date'))
    end = event.get('end', {}).get('dateTime', event.get('end', {}).get('date', 'No date'))
    print(f"\nTitle: {event.get('summary')}")
    print(f"When: {start} to {end}")
    print(f"Where: {event.get('location', 'No location')}")
    if event.get('description'):
        print(f"Description: {event.get('description')[:200]}...")
    print(f"Source: {event.get('extendedProperties', {}).get('private', {}).get('source', 'Unknown')}")
    print("-" * 80) 