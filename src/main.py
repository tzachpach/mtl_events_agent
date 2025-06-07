import sys
import click
from .aggregator import pull_all, process
from .calendar_client import sync

@click.command()
def cli():
    """Montréal Events Agent - Curates and publishes events to Google Calendar."""
    try:
        # Pull events from all sources
        events = pull_all()
        if not events:
            print("No events found")
            sys.exit(0)
            
        # Process events (deduplicate, rank, filter)
        festivals, curated = process(events)
        print(f"Found {len(festivals)} festivals and {len(curated)} curated events")
        
        # Sync to calendar
        sync(festivals + curated)
        print("Successfully synced events to calendar")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    cli() 