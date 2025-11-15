import requests
import os
import json
from datetime import datetime

def fetch_data_from_api(results=10):
    """
    Fetch random user data from the API.
    """
    url = f"https://randomuser.me/api/?results={results}"
    response = requests.get(url)
    data = response.json()
    return data

def save_raw_data(data):
    """
    Save the raw API response into data/raw folder with timestamp.
    """
    os.makedirs("data/raw", exist_ok=True)
    filename = f"raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path = os.path.join("data/raw", filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Raw data saved to {path}")
    return path
