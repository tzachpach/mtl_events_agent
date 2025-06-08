import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
import json

from src.sources.reddit import get_reddit_events
from src.models import Event, EventSource

class TestRedditAdapter(unittest.TestCase):

    @patch('requests.get')
    def test_get_reddit_events_public_feed(self, mock_get):
        # Mock the requests.get response for the public JSON feed
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "Montreal International Jazz Festival 2024",
                            "selftext": "Come join us for a week of amazing jazz music!",
                            "url": "http://jazzfest.com/",
                            "id": "jazzfest123"
                        }
                    },
                    {
                        "data": {
                            "title": "Weekly Meetup: Coffee & Coding Event",
                            "selftext": "A casual gathering for developers.",
                            "url": "http://meetup.com/coding",
                            "id": "codingmeetup456"
                        }
                    },
                    {
                        "data": {
                            "title": "Just a regular post",
                            "selftext": "",
                            "url": "http://reddit.com/post",
                            "id": "regularpost789"
                        }
                    }
                ]
            }
        }

        # Call the function under test
        events = get_reddit_events()

        # Assertions
        self.assertEqual(len(events), 2, "Should return 2 events matching keywords")

        # Check the first event
        event1 = events[0]
        self.assertEqual(event1.title, "Montreal International Jazz Festival 2024")
        self.assertEqual(event1.description, "Come join us for a week of amazing jazz music!")
        self.assertEqual(event1.url, "http://jazzfest.com/")
        self.assertEqual(event1.source, EventSource.REDDIT)
        self.assertEqual(event1.source_id, "jazzfest123")
        self.assertEqual(event1.location, "Montreal")
        self.assertAlmostEqual(event1.duration_hours, 2.0) # start_dt and end_dt are datetime.now() and +2h

        # Check the second event
        event2 = events[1]
        self.assertEqual(event2.title, "Weekly Meetup: Coffee & Coding Event")
        self.assertEqual(event2.description, "A casual gathering for developers.")
        self.assertEqual(event2.url, "http://meetup.com/coding")
        self.assertEqual(event2.source, EventSource.REDDIT)
        self.assertEqual(event2.source_id, "codingmeetup456")
        self.assertEqual(event2.location, "Montreal")
        self.assertAlmostEqual(event2.duration_hours, 2.0)

    @patch('requests.get')
    def test_get_reddit_events_no_posts(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": {"children": []}}
        events = get_reddit_events()
        self.assertEqual(len(events), 0, "Should return an empty list if no posts")

    @patch('requests.get')
    def test_get_reddit_events_http_error(self, mock_get):
        mock_get.return_value.status_code = 404
        mock_get.side_effect = requests.exceptions.HTTPError("Not Found")
        events = get_reddit_events()
        self.assertEqual(len(events), 0, "Should return an empty list on HTTP error")

if __name__ == '__main__':
    unittest.main() 