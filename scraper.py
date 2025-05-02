import requests
from bs4 import BeautifulSoup
import time
import csv 

HEADPHONES_CATEGORY = "https://www.newegg.com/Headphones-Accessories/SubCategory/ID-70"
TEST_URL = HEADPHONES_CATEGORY

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

def fetch_page(url):
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status() 
        print("Success!")
        time.sleep(2) 
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        time.sleep(2)
        return None

html = fetch_page(TEST_URL)
if html:
    print(f"Successfully fetched {len(html)} bytes of HTML.")
else:
    print("Failed to fetch HTML.")