from src.sources import get_all_events
from src.sources.ticketmaster import get_ticketmaster_events
from datetime import datetime

def test_ticketmaster():
    print("\nTesting Ticketmaster source:")
    print("-" * 80)
    
    # Test without API key
    print("Testing without API key (should return empty list):")
    events = get_ticketmaster_events()
    print(f"Found {len(events)} events")
    
    # Test with API key (if available)
    import os
    if os.getenv("TICKETMASTER_API_KEY"):
        print("\nTesting with API key:")
        events = get_ticketmaster_events()
        print(f"Found {len(events)} events")
        if events:
            print("\nSample event:")
            event = events[0]
            print(f"Title: {event.title}")
            print(f"Date: {event.start_dt.strftime('%Y-%m-%d %H:%M')}")
            print(f"Location: {event.location}")
            print(f"URL: {event.url}")
    else:
        print("\nNo API key found - skipping API key test")

def test_all_sources():
    print("\nTesting all event sources:")
    print("-" * 80)
    
    events = get_all_events()
    print(f"\nFound {len(events)} total events")
    
    # Group events by source
    events_by_source = {}
    for event in events:
        source = event.source.value
        if source not in events_by_source:
            events_by_source[source] = []
        events_by_source[source].append(event)
    
    # Print summary by source
    print("\nEvents by source:")
    for source, source_events in events_by_source.items():
        print(f"{source}: {len(source_events)} events")
    
    # Print sample events from each source
    print("\nSample events from each source:")
    for source, source_events in events_by_source.items():
        if source_events:
            event = source_events[0]
            print(f"\n{source.upper()}:")
            print(f"Title: {event.title}")
            print(f"Date: {event.start_dt.strftime('%Y-%m-%d %H:%M')}")
            print(f"Location: {event.location}")
            print(f"URL: {event.url}")

def main():
    print("Starting event source tests...")
    test_ticketmaster()
    test_all_sources()

if __name__ == "__main__":
    main() 