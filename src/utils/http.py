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
    Thin wrapper adding a tiny delay to dodge free-tier throttling.
    
    Args:
        url: The URL to fetch
        headers: Optional HTTP headers
        params: Optional query parameters
        
    Returns:
        JSON response data
        
    Raises:
        requests.exceptions.RequestException: On HTTP errors
    """
    retries = 0
    max_retries = 5
    initial_sleep = 2 # seconds

    while retries < max_retries:
        try:
            resp = requests.get(
                url,
                headers=headers or {},
                params=params or {},
                timeout=10
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [429, 503]:
                sleep_time = initial_sleep * (2 ** retries) # Exponential back-off
                print(f"Rate limit hit (status {e.response.status_code}). Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                retries += 1
            else:
                raise # Re-raise other HTTP errors immediately
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}. Retrying...")
            time.sleep(initial_sleep) # Small delay for other network issues
            retries += 1

    raise requests.exceptions.RequestException(f"Failed to fetch {url} after {max_retries} retries")

def get_csv(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Thin wrapper adding a tiny delay to dodge free-tier throttling and returning a pandas DataFrame.
    
    Args:
        url: The URL to fetch
        headers: Optional HTTP headers
        params: Optional query parameters
        
    Returns:
        pandas DataFrame with CSV data
        
    Raises:
        requests.exceptions.RequestException: On HTTP errors
    """
    retries = 0
    max_retries = 5
    initial_sleep = 2 # seconds

    while retries < max_retries:
        try:
            resp = requests.get(
                url,
                headers=headers or {},
                params=params or {},
                timeout=10
            )
            resp.raise_for_status()
            return pd.read_csv(io.StringIO(resp.text))
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [429, 503]:
                sleep_time = initial_sleep * (2 ** retries) # Exponential back-off
                print(f"Rate limit hit (status {e.response.status_code}). Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                retries += 1
            else:
                raise # Re-raise other HTTP errors immediately
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}. Retrying...")
            time.sleep(initial_sleep) # Small delay for other network issues
            retries += 1

    raise requests.exceptions.RequestException(f"Failed to fetch {url} after {max_retries} retries") 