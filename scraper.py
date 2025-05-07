from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import time
import re
import urllib.parse

BASE_URL = "https://www.newegg.com"
category_url = (
    "https://www.newegg.com/Headphones-Accessories/SubCategory/ID-70?PageSize=96"
)
MAX_PRODUCTS = 500

PRODUCT_LINK = "div.item-container a.item-title"
NEXT_PAGE_LINK = 'a[title="Next"]'

product_urls = [
    {
        "id": 1,
        "url": "https://www.newegg.com/grey-beyerdynamic-dt-770-pro-over-the-ear/p/0TH-00JD-000K8",
    },
    {
        "id": 2,
        "url": "https://www.newegg.com/bose-884367-0100-headphone-black/p/N82E16826627141",
    },
    {
        "id": 3,
        "url": "https://www.newegg.com/bose-880066-0100-headphone-black/p/N82E16826627143",
    },
]


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

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

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


def extract_links_and_next_page(html_content):
    if not html_content:
        return set(), None

    soup = BeautifulSoup(html_content, "lxml")
    product_links = set()
    next_page_url = None

    link_elements = soup.select(PRODUCT_LINK)
    print(f"  Found {len(link_elements)} potential product link elements.")
    for link in link_elements:
        if link.has_attr("href"):
            href = link["href"]
            if href.lower().startswith("javascript:"):
                continue
            absolute_url = urllib.parse.urljoin(BASE_URL, href)
            if "/p/" in urllib.parse.urlparse(absolute_url).path:
                product_links.add(absolute_url)

    next_page_element = soup.select_one(NEXT_PAGE_LINK)
    if next_page_element and next_page_element.has_attr("href"):
        next_href = next_page_element["href"]
        if not next_href.lower().startswith("javascript:"):
            next_page_url = urllib.parse.urljoin(BASE_URL, next_href)

    print(f"  Extracted {len(product_links)} product URLs from this page. Ex. link: {list(product_links)[:7]}")
    print(f"  Next page URL found: {next_page_url}")

    return product_links, next_page_url

def parse_product_data(html_content):
    if not html_content:
        return None
    soup = BeautifulSoup(html_content, "lxml")
    data = {}

    title_element = soup.select_one("h1.product-title")
    data["product_title"] = (
        title_element.get_text(strip=True) if title_element else None
    )

    price_element = soup.select_one("div.price-current")
    if price_element and price_element.strong and price_element.sup:
        dollars = price_element.strong.get_text(strip=True)
        cents = price_element.sup.get_text(strip=True)
        data["product_price"] = f"{dollars}{cents}"
    else:
        data["product_price"] = None

    seller_element = soup.select_one("div.product-seller-sold-by strong")
    data["seller_name"] = (
        seller_element.get_text(strip=True) if seller_element else None
    )

    bullet_items = soup.select("div.product-bullets ul li")
    data["product_description"] = (
        "\n".join(li.get_text(strip=True) for li in bullet_items)
        if bullet_items
        else None
    )

    rating_element = soup.select_one("div.product-rating i.rating")
    if rating_element and "title" in rating_element.attrs:
        rating_text = rating_element["title"]
        match = re.search(r"([\d.]+) out of 5", rating_text)
        data["product_rating"] = float(match.group(1)) if match else None
    else:
        data["product_rating"] = None

    img_element = soup.select_one("img.product-view-img-original")
    data["main_image_url"] = (
        img_element["src"] if img_element and "src" in img_element.attrs else None
    )

    return data


CSV_FILE = "headphone_products.csv"
FIELDNAMES = [
    "product_title",
    "product_description",
    "product_price",
    "product_rating",
    "seller_name",
    "main_image_url",
]

try:
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
    print(f"CSV header written to {CSV_FILE}")
except IOError as e:
    print(f"Error initializing CSV file: {e}")

products_scraped_count = 0

for product in product_urls:
    product_id = product.get("id", "N/A")
    url = product.get("url")

    if not url:
        print(f"  Skipping entry with ID {product_id} due to missing URL.")
        continue

    print(f"Processing ID {product_id}: {url}")

    html = fetch_page_with_selenium(url)

    if html:
        product_info = parse_product_data(html)

        if product_info:
            print(f"  Successfully parsed: {product_info.get('product_title', 'N/A')}")

            product_info["original_id"] = product_id

            try:
                with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(
                        f, fieldnames=FIELDNAMES, extrasaction="ignore"
                    )
                    writer.writerow(product_info)
                products_scraped_count += 1
            except IOError as e:
                print(f"  Error writing row to CSV for ID {product_id} ({url}): {e}")
            except Exception as e:
                print(
                    f"  Unexpected error writing row for ID {product_id} ({url}): {e}"
                )
        else:
            print(f"  Could not parse data for ID {product_id} ({url})")

print(f"Successfully scraped and wrote {products_scraped_count} products to {CSV_FILE}")
