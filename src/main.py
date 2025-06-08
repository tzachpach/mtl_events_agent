import sys
import click
import time
import src.aggregator as aggregator
import src.calendar_client as calendar_client

T0 = time.time()
def log(msg: str): print(f"[{time.time()-T0:5.1f}s] {msg}", flush=True)

@click.command()
def cli():
    """Montréal Events Agent - Curates and publishes events to Google Calendar."""
    try:
        # Pull events from all sources
        log("Fetching events from all sources")
        events = aggregator.pull_all()
        log(f"Fetched {len(events)} total events from all sources")

        if not events:
            log("No events found")
            sys.exit(0)
            
        # Process events (deduplicate, rank, filter)
        log("Ranking / filtering events")
        festivals, curated = aggregator.process(events)
        log(f"Found {len(festivals)} festivals and {len(curated)} curated events")
        
        # Sync to calendar
        log("Syncing events to Calendar")
        calendar_client.sync(festivals + curated)
        log("Successfully synced events to calendar")
        
    except Exception as e:
        log(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    cli() 