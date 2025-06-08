import time
import requests
from typing import Optional, Dict, Any, List
import pandas as pd
import io
import csv

def fetch_csv(url: str, timeout: int = 10, max_bytes: int = 5_000_000) -> List[Dict]:
    """
    Stream-download a CSV with a hard timeout and size cap.
    Returns a list of dict rows. Raises on timeout or >max_bytes.
    """
    r = requests.get(url, stream=True, timeout=timeout)
    r.raise_for_status()
    raw = io.BytesIO()
    for chunk in r.iter_content(1024):
        raw.write(chunk)
        if raw.tell() > max_bytes:
            raise RuntimeError("CSV too large")
    raw.seek(0)
    return list(csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8")))

def get_json(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Thin wrapper with timeout and single retry for 429.
    
    Args:
        url: The URL to fetch
        headers: Optional HTTP headers
        params: Optional query parameters
        
    Returns:
        JSON response data
        
    Raises:
        requests.exceptions.RequestException: On HTTP errors
    """
    resp = requests.get(
        url,
        headers=headers or {},
        params=params or {},
        timeout=10
    )
    if resp.status_code == 429:
        print(f"Rate limit hit (status 429). Retrying after 2 seconds...")
        time.sleep(2)
        resp = requests.get(
            url,
            headers=headers or {},
            params=params or {},
            timeout=10
        )
    resp.raise_for_status()
    return resp.json()

def get_csv(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Thin wrapper with timeout and single retry for 429, returning a pandas DataFrame.
    
    Args:
        url: The URL to fetch
        headers: Optional HTTP headers
        params: Optional query parameters
        
    Returns:
        pandas DataFrame with CSV data
        
    Raises:
        requests.exceptions.RequestException: On HTTP errors
    """
    resp = requests.get(
        url,
        headers=headers or {},
        params=params or {},
        timeout=10
    )
    if resp.status_code == 429:
        print(f"Rate limit hit (status 429). Retrying after 2 seconds...")
        time.sleep(2)
        resp = requests.get(
            url,
            headers=headers or {},
            params=params or {},
            timeout=10
        )
    resp.raise_for_status()
    return pd.read_csv(io.StringIO(resp.text)) 