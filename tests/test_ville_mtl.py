from typing import List
from datetime import datetime, timedelta
import pandas as pd
import pytest
from unittest.mock import patch

from src.models import Event, EventSource
from src.sources.ville_mtl import get_city_events
from src.utils.http import get_csv

def test_get_city_events():
    # Use dates that are within the next 35 days from now
    today = datetime.now()
    event1_start_date = (today + timedelta(days=5)).isoformat(timespec='minutes')
    event1_end_date = (today + timedelta(days=5, hours=2)).isoformat(timespec='minutes')
    event2_start_date = (today + timedelta(days=10)).isoformat(timespec='minutes')
    event2_end_date = (today + timedelta(days=10, hours=2)).isoformat(timespec='minutes')

    # Mock CSV content with two rows, ensuring `titre_adresse` and `arrondissement` are present for location
    mock_csv_content = (
        "titre,description,url_fiche,date_debut,date_fin,titre_adresse,arrondissement\n"
        f"Event 1,Description 1,http://example.com/event1,{event1_start_date},{event1_end_date},Address 1,Downtown\n"
        f"Event 2,Description 2,http://example.com/event2,{event2_start_date},{event2_end_date},Address 2,Plateau"
    )

    # Mock the get_csv function to return a pandas DataFrame from the mock CSV content
    with patch('src.utils.http.get_csv', return_value=pd.read_csv(pd.io.common.StringIO(mock_csv_content))):
        events = get_city_events()

        assert isinstance(events, List)
        assert len(events) == 2

        # Assert properties of the first event
        event1 = events[0]
        assert event1.title == "Event 1"
        assert event1.description == "Description 1"
        assert event1.url == "http://example.com/event1"
        # Note: isoformat() might include microseconds, so compare dates without them
        assert event1.start_dt.replace(microsecond=0) == datetime.fromisoformat(event1_start_date).replace(microsecond=0)
        assert event1.end_dt.replace(microsecond=0) == datetime.fromisoformat(event1_end_date).replace(microsecond=0)
        assert event1.location == "Address 1"
        assert event1.source == EventSource.VILLE_MTL
        assert event1.source_id == "http://example.com/event1"
        assert event1.is_all_day == False # Based on 2-hour duration
        assert event1.popularity == 0.2

        # Assert properties of the second event
        event2 = events[1]
        assert event2.title == "Event 2"
        assert event2.description == "Description 2"
        assert event2.url == "http://example.com/event2"
        assert event2.start_dt.replace(microsecond=0) == datetime.fromisoformat(event2_start_date).replace(microsecond=0)
        assert event2.end_dt.replace(microsecond=0) == datetime.fromisoformat(event2_end_date).replace(microsecond=0)
        assert event2.location == "Address 2"
        assert event2.source == EventSource.VILLE_MTL
        assert event2.source_id == "http://example.com/event2"
        assert event2.is_all_day == False
        assert event2.popularity == 0.2 