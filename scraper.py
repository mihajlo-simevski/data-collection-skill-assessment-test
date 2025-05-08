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
STARTING_CATEGORY_URL = (
    "https://www.newegg.com/Headphones-Accessories/SubCategory/ID-70?PageSize=96"
)
MAX_PRODUCTS = 500

PRODUCT_LINK = "div.item-container a.item-title"
NEXT_PAGE_LINK = 'a[title="Next"]'

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

collected_product_urls = set()
visited_category_urls = set()
current_category_url = STARTING_CATEGORY_URL
page_count = 1

while len(collected_product_urls) < MAX_PRODUCTS and current_category_url:
    if current_category_url in visited_category_urls:
        print(f"Stopping collection: Already visited {current_category_url}")
        break
    visited_category_urls.add(current_category_url)

    print(f"\nProcessing Category Page {page_count}: {current_category_url}")
    print(f"Collected {len(collected_product_urls)} URLs so far (Target: {MAX_PRODUCTS})")

    category_html = fetch_page_with_selenium(current_category_url)

    if category_html:
        new_links, next_page = extract_links_and_next_page(category_html)

        original_count = len(collected_product_urls)
        collected_product_urls.update(new_links)
        added_count = len(collected_product_urls) - original_count
        print(f"  Added {added_count} new unique product URLs.")

        current_category_url = next_page
        page_count += 1

        if not current_category_url:
            print("No more 'Next Page' links found. Stopping collection.")
            break
        if len(collected_product_urls) >= MAX_PRODUCTS:
             print(f"Reached target of {MAX_PRODUCTS} products. Stopping collection.")
             break

    else:
        print(f"Failed to fetch category page {current_category_url}. Stopping collection.")
        break

print(f"\n--- URL Collection Finished ---")
print(f"Collected a total of {len(collected_product_urls)} unique product URLs.")

product_urls_to_scrape = list(collected_product_urls)[:MAX_PRODUCTS]
print(f"Proceeding to scrape the first {len(product_urls_to_scrape)} products.")

products_scraped_count = 0

for url in product_urls_to_scrape:

    html = fetch_page_with_selenium(url)

    if html:
        product_info = parse_product_data(html)

        if product_info:
            print(f"  Successfully parsed: {product_info.get('product_title', 'N/A')}")

            try:
                with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(
                        f, fieldnames=FIELDNAMES, extrasaction="ignore"
                    )
                    writer.writerow(product_info)
                products_scraped_count += 1
            except IOError as e:
                print(f"  Error writing row to CSV for ID  ({url}): {e}")
            except Exception as e:
                print(
                    f"  Unexpected error writing row for ID ({url}): {e}"
                )
        else:
            print(f"  Could not parse data for ID ({url})")

print(f"Successfully scraped and wrote {products_scraped_count} products to {CSV_FILE}")
