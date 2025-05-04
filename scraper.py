from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import time
import re

HEADPHONES_URL = "https://www.newegg.com/grey-beyerdynamic-dt-770-pro-over-the-ear/p/0TH-00JD-000K8"

def fetch_page_with_selenium(url):
    print(f"Fetching {url} with headless browser...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(3)
        html = driver.page_source
        print("Success!")
        return html
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None
    finally:
        driver.quit()

def parse_product_data(html_content):
    if not html_content:
        return None
    soup = BeautifulSoup(html_content, 'lxml')
    data = {}

    title_element = soup.select_one('h1.product-title')
    data['product_title'] = title_element.get_text(strip=True) if title_element else None

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
    data['product_description'] = '\n'.join(li.get_text(strip=True) for li in bullet_items) if bullet_items else None

    rating_element = soup.select_one('div.product-rating i.rating')
    if rating_element and 'title' in rating_element.attrs:
        rating_text = rating_element['title']
        match = re.search(r'([\d.]+) out of 5', rating_text)
        data['product_rating'] = float(match.group(1)) if match else None
    else:
        data['product_rating'] = None

    img_element = soup.select_one('img.product-view-img-original')
    data['main_image_url'] = img_element['src'] if img_element and 'src' in img_element.attrs else None

    return data

html = fetch_page_with_selenium(HEADPHONES_URL)
if html:
    product_info = parse_product_data(html)
    print("\nExtracted Data (Partial):")
    for key, value in product_info.items():
        print(f"{key}:")
        print(value if value else "  (not found)")
        print()
else:
    print("Failed to fetch HTML.")


CSV_FILE = 'headphone_products.csv'
FIELDNAMES = [
    'product_title',
    'product_description',
    'product_price',
    'product_rating',
    'seller_name',
    'main_image_url',
]

with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    print(f"CSV header written to {CSV_FILE}")