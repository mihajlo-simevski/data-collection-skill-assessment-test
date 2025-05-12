import logging
from typing import Set

from config import (
    STARTING_CATEGORY_URL,
    MAX_PRODUCTS_TO_SCRAPE,
    CSV_FILE_NAME,
    CSV_FIELDNAMES,
)
from webdriver_utils import init_driver, fetch_page_content, quit_driver
from link_extractor import extract_product_urls_and_next_page
from product_parser import parse_product_page_details
from csv_handler import initialize_csv, append_to_csv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)


def main():
    logging.info("Starting Newegg Product Scraper...")

    driver = init_driver()
    if not driver:
        logging.critical("WebDriver could not be initialized. Exiting.")
        return

    try:
        initialize_csv(CSV_FILE_NAME, CSV_FIELDNAMES)
    except Exception:
        logging.critical(f"Could not initialize CSV file {CSV_FILE_NAME}. Exiting.")
        quit_driver(driver)
        return

    collected_product_urls: Set[str] = set()
    visited_category_urls: Set[str] = set()
    current_category_url: str | None = STARTING_CATEGORY_URL
    category_page_count = 1

    # --- Phase 1: Collect Product URLs ---
    logging.info("--- Starting URL Collection Phase ---")
    while len(collected_product_urls) < MAX_PRODUCTS_TO_SCRAPE and current_category_url:
        if current_category_url in visited_category_urls:
            logging.warning(
                f"Already visited category URL: {current_category_url}. Stopping to prevent loop."
            )
            break
        visited_category_urls.add(current_category_url)

        logging.info(
            f"Processing Category Page {category_page_count}: {current_category_url}"
        )
        logging.info(
            f"Collected {len(collected_product_urls)} URLs so far (Target: {MAX_PRODUCTS_TO_SCRAPE})"
        )

        category_html = fetch_page_content(driver, current_category_url)
        if category_html:
            new_links, next_page_from_parser = extract_product_urls_and_next_page(
                category_html
            )

            original_count = len(collected_product_urls)
            collected_product_urls.update(new_links)
            added_count = len(collected_product_urls) - original_count
            logging.info(f"Added {added_count} new unique product URLs from this page.")
            if new_links:
                logging.debug(f"Example new links: {list(new_links)[:3]}")

            current_category_url = next_page_from_parser
            category_page_count += 1

            if not current_category_url:
                logging.info("No more 'Next Page' links found on category pages.")
                break
            if len(collected_product_urls) >= MAX_PRODUCTS_TO_SCRAPE:
                logging.info(
                    f"Reached or exceeded target of {MAX_PRODUCTS_TO_SCRAPE} product URLs."
                )
                break
        else:
            logging.error(
                f"Failed to fetch category page {current_category_url}. Stopping URL collection."
            )
            break

    logging.info("--- URL Collection Finished ---")
    logging.info(
        f"Collected a total of {len(collected_product_urls)} unique product URLs."
    )

    # --- Phase 2: Scrape Product Details ---
    product_urls_to_scrape = list(collected_product_urls)[:MAX_PRODUCTS_TO_SCRAPE]
    logging.info(
        f"--- Starting Product Data Scraping Phase for {len(product_urls_to_scrape)} products ---"
    )

    products_scraped_count = 0
    for i, product_url in enumerate(product_urls_to_scrape):
        logging.info(
            f"Scraping product {i+1}/{len(product_urls_to_scrape)}: {product_url}"
        )
        product_html = fetch_page_content(driver, product_url)

        if product_html:
            product_info = parse_product_page_details(product_html)
            if product_info:
                logging.info(
                    f"  Successfully parsed: {product_info.get('product_title', 'N/A')}"
                )
                append_to_csv(CSV_FILE_NAME, CSV_FIELDNAMES, product_info)
                products_scraped_count += 1
            else:
                logging.warning(
                    f"  Could not parse data for product URL: {product_url}"
                )
        else:
            logging.error(f"  Failed to fetch HTML for product URL: {product_url}")

    logging.info("--- Product Data Scraping Finished ---")
    logging.info(
        f"Successfully scraped and wrote {products_scraped_count} products to {CSV_FILE_NAME}"
    )

    quit_driver(driver)
    logging.info("Scraping process completed.")


if __name__ == "__main__":
    main()
