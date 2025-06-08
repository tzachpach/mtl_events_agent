import sys
import click
import time
import src.aggregator as aggregator
import src.calendar_client as calendar_client

T0 = time.time()
def log(msg: str): print(f"[{time.time()-T0:6.1f}s] {msg}", flush=True)

@click.command()
def cli():
    """Montréal Events Agent - Curates and publishes events to Google Calendar."""
    try:
        # Pull events from all sources
        log("Fetching events from all sources")
        events = aggregator.pull_all()
        log(f"pull_all returned {len(events)} rows")

        if not events:
            log("No events found")
            sys.exit(0)
            
        # Process events (deduplicate, rank, filter)
        log("Ranking / filtering events")
        festivals, curated = aggregator.process(events)
        log(f"Ranked to {len(festivals)} festivals + {len(curated)} curated")
        
        # Sync to calendar
        log("Syncing to Google Calendar")
        calendar_client.sync(festivals + curated)
        log("Done")
        
    except Exception as e:
        log(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    cli() 