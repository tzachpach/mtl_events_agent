import time
import requests
from typing import Optional, Dict, Any
import pandas as pd
import io

def get_json(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    pause: float = 0.2
) -> Dict[str, Any]:
    """
    Thin wrapper adding a tiny delay to dodge free-tier throttling.
    
    Args:
        url: The URL to fetch
        headers: Optional HTTP headers
        params: Optional query parameters
        pause: Delay in seconds between requests
        
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
    time.sleep(pause)
    resp.raise_for_status()
    return resp.json()

def get_csv(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    pause: float = 0.2
) -> pd.DataFrame:
    """
    Thin wrapper adding a tiny delay to dodge free-tier throttling and returning a pandas DataFrame.
    
    Args:
        url: The URL to fetch
        headers: Optional HTTP headers
        params: Optional query parameters
        pause: Delay in seconds between requests
        
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
    time.sleep(pause)
    resp.raise_for_status()
    return pd.read_csv(io.StringIO(resp.text)) 