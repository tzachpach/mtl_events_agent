import sys
import click
import time
import os
import src.aggregator as aggregator
import src.calendar_client as calendar_client
from datetime import datetime
from .aggregator import pull_all
from .ranker import rank_events
from .calendar_client import sync

T0 = time.time()
def log(msg: str): print(f"[{time.time()-T0:6.1f}s] {msg}", flush=True)

@click.command()
def cli():
    """Montréal Events Agent - Curates and publishes events to Google Calendar."""
    try:
        print("Starting event aggregator...")
        print(f"Using calendar ID: {os.getenv('GOOGLE_CALENDAR_ID')}")
        print(f"Service account file path: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
        
        if os.path.isfile(os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')):
            with open(os.getenv('GOOGLE_APPLICATION_CREDENTIALS', ''), 'r') as f:
                print("Service account file contents:")
                for line in f:
                    if "client_email" in line:
                        print(f"  {line.strip()}")
                        break
        
        start_time = time.time()
        print(f"\n[{time.time() - start_time:.1f}s] Fetching events from all sources")
        events = pull_all()
        fetch_time = time.time()
        print(f"[{fetch_time - start_time:.1f}s] Fetched {len(events)} total events")
        
        print(f"\n[{time.time() - start_time:.1f}s] Ranking events")
        ranked = rank_events(events)
        rank_time = time.time()
        print(f"[{rank_time - fetch_time:.1f}s] Ranked {len(ranked)} events")
        
        print(f"\n[{time.time() - start_time:.1f}s] Syncing to calendar")
        sync(ranked)
        sync_time = time.time()
        print(f"[{sync_time - rank_time:.1f}s] Calendar sync complete")
        
        print(f"\nTotal time: {sync_time - start_time:.1f}s")
        
    except Exception as e:
        log(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    cli() 