import sys
import click
import time
import src.aggregator as aggregator
import src.calendar_client as calendar_client
from datetime import datetime

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
        
        # Display top 20 events
        log("\nTop 20 Curated Events:")
        for i, event in enumerate(curated[:20], 1):
            log(f"\n{i}. {event.title}")
            log(f"   When: {event.start_dt.strftime('%Y-%m-%d %H:%M')} - {event.end_dt.strftime('%H:%M')}")
            log(f"   Where: {event.location}")
            log(f"   Source: {event.source.value}")
            if event.score:
                log(f"   Score: {event.score:.2f}")
            if event.popularity:
                log(f"   Popularity: {event.popularity:.2f}")
        
        if festivals:
            log("\nFestivals/Multi-day Events:")
            for i, event in enumerate(festivals[:5], 1):
                log(f"\n{i}. {event.title}")
                log(f"   When: {event.start_dt.strftime('%Y-%m-%d')} - {event.end_dt.strftime('%Y-%m-%d')}")
                log(f"   Where: {event.location}")
                log(f"   Source: {event.source.value}")

        # Sync events to calendar
        log("\nSyncing events to calendar...")
        all_events = festivals + curated
        calendar_client.sync(all_events)
        log("Calendar sync complete")
        
    except Exception as e:
        log(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    cli() 