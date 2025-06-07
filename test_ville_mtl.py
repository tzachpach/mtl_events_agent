from src.sources.ville_mtl import get_city_events
from datetime import datetime

def main():
    print("Fetching Ville de Montréal events...")
    events = get_city_events()
    
    print(f"\nFound {len(events)} events:")
    print("-" * 80)
    
    for event in events:
        print(f"Title: {event.title}")
        print(f"Date: {event.start_dt.strftime('%Y-%m-%d %H:%M')} to {event.end_dt.strftime('%Y-%m-%d %H:%M')}")
        print(f"Location: {event.location}")
        print(f"URL: {event.url}")
        print(f"All day: {event.is_all_day}")
        print(f"Popularity: {event.popularity}")
        print("-" * 80)

if __name__ == "__main__":
    main() 