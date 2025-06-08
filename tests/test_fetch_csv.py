from src.utils.http import fetch_csv
import pytest, requests

def test_timeout(monkeypatch):
    def slow_get(*_, **__): raise requests.Timeout()
    monkeypatch.setattr(requests, "get", slow_get)
    with pytest.raises(requests.Timeout):
        fetch_csv("http://example.com/file.csv", timeout=1) 