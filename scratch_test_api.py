import sys
import json
import urllib.request
import urllib.parse
from urllib.error import HTTPError

BASE_URL = "https://emova-api-490638015196.us-central1.run.app"

def test_api():
    print("Testing connection to API...")
    try:
        req = urllib.request.Request(f"{BASE_URL}/docs")
        response = urllib.request.urlopen(req)
        print("API is reachable. Status:", response.status)
    except Exception as e:
        print("Failed to reach API:", e)

if __name__ == "__main__":
    test_api()
