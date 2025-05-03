import requests
from bs4 import BeautifulSoup
import time
import csv
import re 

HEADPHONES_CATEGORY = "https://www.newegg.com/grey-beyerdynamic-dt-770-pro-over-the-ear/p/0TH-00JD-000K8"
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


def parse_product_data(html_content):
    if not html_content:
        return None
    soup = BeautifulSoup(html_content, 'lxml')
    data = {}

    title_element = soup.select_one('h1.product-title')
    data['product title'] = title_element.get_text(strip=True) if title_element else None

    price_element = soup.select_one('div.price-current')
    if price_element and price_element.strong and price_element.sup:
        dollars = price_element.strong.get_text(strip=True)
        cents = price_element.sup.get_text(strip=True)
        data['product_price'] = f"{dollars}{cents}"
    else:
        data['product_price'] = None

    seller_element = soup.select_one('div.product-seller-sold-by strong')
    data['seller_name'] = seller_element.get_text(strip=True) if seller_element else None

    bullet_items = soup.select('div.product-bullets ul li')
    data['product description'] = '\n'.join(li.get_text(strip=True) for li in bullet_items) if bullet_items else None


    rating_element = soup.select_one('div.product-rating i.rating')
    if rating_element and 'title' in rating_element.attrs:
        rating_text = rating_element['title']
        match = re.search(r'([\d.]+) out of 5', rating_text)
        data['product rating'] = float(match.group(1)) if match else None
    else:
        data['product rating'] = None


    img_element = soup.select_one('img.product-view-img-original')
    data['Main Image URL'] = img_element['src'] if img_element and 'src' in img_element.attrs else None


    return data 


html = fetch_page(TEST_URL)
if html:
    product_info = parse_product_data(html)
    print("\nExtracted Data (Partial):")
    for key, value in product_info.items():
        print(f"{key}:")
        print(value if value else "  (not found)")
        print()