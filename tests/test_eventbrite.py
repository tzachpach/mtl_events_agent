# EVENTBRITE TEST DISABLED FOR NOW
#
# import os
# import pytest
# from unittest.mock import patch
# from src.sources.eventbrite import get_eventbrite_events
#
# @pytest.fixture
# def mock_env():
#     with patch.dict(os.environ, {"EVENTBRITE_TOKEN": "dummy_token"}):
#         yield
#
# @pytest.fixture
# def mock_get_json():
#     with patch("src.sources.eventbrite.get_json") as mock:
#         mock.return_value = {"events": []}
#         yield mock
#
# def test_get_eventbrite_events(mock_env, mock_get_json):
#     events = get_eventbrite_events()
#     assert isinstance(events, list)
#     mock_get_json.assert_called_once() 