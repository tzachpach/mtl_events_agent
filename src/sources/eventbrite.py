# EVENTBRITE ADAPTER DISABLED FOR NOW
#
# from typing import List
# import os
# from datetime import datetime, timedelta
# from ..models import Event, EventSource
# from ..utils.http import get_json
#
# EVENTBRITE_API_URL = "https://www.eventbriteapi.com/v3"
#
# def get_eventbrite_events() -> List[Event]:
#     """
#     Fetch events from Eventbrite API.
#     
#     Returns:
#         List of Event objects
#     """
#     EVENTBRITE_TOKEN = os.getenv("EVENTBRITE_TOKEN")
#     if not EVENTBRITE_TOKEN:
#         raise ValueError("EVENTBRITE_TOKEN environment variable not set")
#         
#     # Calculate date range (next 30 days)
#     start_date = datetime.now()
#     end_date = start_date + timedelta(days=30)
#     
#     # Build API request
#     params = {
#         "location.address": "Montreal, QC, Canada",
#         "start_date.range_start": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
#         "start_date.range_end": end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
#         "expand": "venue",
#         "sort_by": "date",
#     }
#     
#     headers = {
#         "Authorization": f"Bearer {EVENTBRITE_TOKEN}",
#         "Accept": "application/json",
#     }
#     
#     # Make API request
#     data = get_json(
#         f"{EVENTBRITE_API_URL}/events/search/",
#         headers=headers,
#         params=params
#     )
#     
#     # Parse response
#     events = []
#     for event_data in data["events"]:
#         try:
#             # Skip past events
#             start_dt = datetime.fromisoformat(event_data["start"]["local"].replace("Z", "+00:00"))
#             if start_dt < datetime.now():
#                 continue
#                 
#             # Create Event object
#             event = Event(
#                 title=event_data["name"]["text"],
#                 description=event_data["description"]["text"],
#                 start_dt=start_dt,
#                 end_dt=datetime.fromisoformat(event_data["end"]["local"].replace("Z", "+00:00")),
#                 location=event_data["venue"]["name"] if event_data.get("venue") else "TBD",
#                 url=event_data["url"],
#                 source=EventSource.EVENTBRITE,
#                 source_id=event_data["id"],
#                 is_all_day=event_data.get("is_series_parent", False),
#                 popularity=float(event_data.get("popularity", 0))
#             )
#             events.append(event)
#             
#         except (KeyError, ValueError) as e:
#             print(f"Error parsing Eventbrite event {event_data.get('id', 'unknown')}: {e}")
#             continue
#             
#     return events 