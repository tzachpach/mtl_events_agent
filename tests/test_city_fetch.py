import unittest
from unittest.mock import patch, MagicMock
import io
import requests
from src.utils.http import fetch_csv

class TestFetchCsv(unittest.TestCase):

    def setUp(self):
        self.small_csv_content = (
            "header1,header2\n"
            "value1a,value1b\n"
            "value2a,value2b\n"
        ).encode('utf-8')
        
        self.large_csv_content = b'a' * 10_000_000 # 10MB

    @patch('requests.get')
    def test_fetch_csv_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [self.small_csv_content]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        rows = fetch_csv("http://example.com/small.csv")
        self.assertEqual(len(rows), 2) # Excludes header
        self.assertEqual(rows[0]["header1"], "value1a")
        self.assertEqual(rows[1]["header2"], "value2b")

        mock_get.assert_called_once_with("http://example.com/small.csv", stream=True, timeout=10)

    @patch('requests.get')
    def test_fetch_csv_too_large(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Simulate streaming chunks larger than max_bytes
        mock_response.iter_content.return_value = [self.large_csv_content]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with self.assertRaisesRegex(RuntimeError, "CSV too large"):
            fetch_csv("http://example.com/large.csv", max_bytes=5_000_000) # 5MB cap

        mock_get.assert_called_once_with("http://example.com/large.csv", stream=True, timeout=10)

    @patch('requests.get')
    def test_fetch_csv_http_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.HTTPError("Not Found")

        with self.assertRaises(requests.exceptions.HTTPError):
            fetch_csv("http://example.com/error.csv")

        mock_get.assert_called_once_with("http://example.com/error.csv", stream=True, timeout=10)

if __name__ == '__main__':
    unittest.main() 