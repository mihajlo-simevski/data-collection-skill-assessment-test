import urllib.parse
import logging
from bs4 import BeautifulSoup
from typing import Set, Tuple, Optional

from config import BASE_URL, PRODUCT_LINK_SELECTOR, NEXT_PAGE_LINK_SELECTOR


def extract_product_urls_and_next_page(
    html_content: Optional[str],
) -> Tuple[Set[str], Optional[str]]:
    if not html_content:
        logging.debug("No HTML content provided to extract_product_urls_and_next_page.")
        return set(), None

    soup = BeautifulSoup(html_content, "lxml")
    product_links: Set[str] = set()
    next_page_url: Optional[str] = None

    link_elements = soup.select(PRODUCT_LINK_SELECTOR)
    logging.debug(
        f"Found {len(link_elements)} potential product link elements in link_extractor."
    )
    for link in link_elements:
        if link.has_attr("href"):
            href = link["href"]
            if href.lower().startswith("javascript:"):
                continue
            absolute_url = urllib.parse.urljoin(BASE_URL, href)
            if "/p/" in urllib.parse.urlparse(absolute_url).path:
                product_links.add(absolute_url)

    next_page_element = soup.select_one(NEXT_PAGE_LINK_SELECTOR)
    if next_page_element and next_page_element.has_attr("href"):
        next_href = next_page_element["href"]
        if not next_href.lower().startswith("javascript:"):
            next_page_url = urllib.parse.urljoin(BASE_URL, next_href)

    logging.debug(
        f"Extracted {len(product_links)} product URLs. Next page: {next_page_url}"
    )
    return product_links, next_page_url
