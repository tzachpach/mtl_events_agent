import time
import requests
from typing import Optional, Dict, Any
import pandas as pd
import io

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