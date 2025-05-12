import re
import logging
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional

from config import (
    PRODUCT_TITLE_SELECTOR,
    PRODUCT_PRICE_SELECTOR,
    PRODUCT_PRICE_DOLLARS_SELECTOR,
    PRODUCT_PRICE_CENTS_SELECTOR,
    PRODUCT_SELLER_SELECTOR,
    PRODUCT_DESCRIPTION_BULLETS_SELECTOR,
    PRODUCT_RATING_SELECTOR,
    PRODUCT_IMAGE_SELECTOR,
)


def parse_product_page_details(html_content: Optional[str]) -> Optional[Dict[str, Any]]:
    if not html_content:
        logging.debug("No HTML content provided to parse_product_page_details.")
        return None

    soup = BeautifulSoup(html_content, "lxml")
    data: Dict[str, Any] = {}

    title_element = soup.select_one(PRODUCT_TITLE_SELECTOR)
    data["product_title"] = (
        title_element.get_text(strip=True) if title_element else None
    )

    price_container = soup.select_one(PRODUCT_PRICE_SELECTOR)
    if price_container:
        dollars_el = price_container.select_one(PRODUCT_PRICE_DOLLARS_SELECTOR)
        cents_el = price_container.select_one(PRODUCT_PRICE_CENTS_SELECTOR)
        if dollars_el and cents_el:
            dollars = dollars_el.get_text(strip=True)
            cents = cents_el.get_text(strip=True)
            data["product_price"] = f"{dollars}{cents}"
        elif dollars_el:
            data["product_price"] = dollars_el.get_text(strip=True)
        else:
            data["product_price"] = None

    seller_element = soup.select_one(PRODUCT_SELLER_SELECTOR)
    if seller_element:
        data["seller_name"] = seller_element.get_text(strip=True)
    else:
        data["seller_name"] = None

    bullet_items = soup.select(PRODUCT_DESCRIPTION_BULLETS_SELECTOR)
    data["product_description"] = (
        "\n".join(li.get_text(strip=True) for li in bullet_items)
        if bullet_items
        else None
    )

    rating_element = soup.select_one(PRODUCT_RATING_SELECTOR)
    if rating_element and "title" in rating_element.attrs:
        rating_text = rating_element["title"]
        match = re.search(r"([\d.]+)(?: out of 5)?", rating_text)
        data["product_rating"] = float(match.group(1)) if match else None
    else:
        data["product_rating"] = None

    img_element = soup.select_one(PRODUCT_IMAGE_SELECTOR)
    if img_element and "src" in img_element.attrs:
        data["main_image_url"] = img_element["src"]
    else:
        data["main_image_url"] = None

    return data
