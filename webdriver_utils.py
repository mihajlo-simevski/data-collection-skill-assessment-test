import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from config import (
    HEADLESS_BROWSER,
    USER_AGENT,
    WINDOW_SIZE,
    SELENIUM_WAIT_TIMEOUT,
    PAGE_LOAD_SLEEP,
)


def init_driver():
    logging.info("Initializing WebDriver...")
    options = Options()
    if HEADLESS_BROWSER:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument(f"window-size={WINDOW_SIZE}")
    options.add_argument(f"user-agent={USER_AGENT}")

    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    try:
        driver_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=driver_service, options=options)
        logging.info("WebDriver initialized successfully.")
        return driver
    except Exception as e:
        logging.error(f"Error initializing WebDriver: {e}")
        return None


def fetch_page_content(driver, url: str) -> str | None:
    if not driver:
        logging.error("WebDriver not initialized. Cannot fetch page.")
        return None

    logging.info(f"Fetching {url}...")
    try:
        driver.get(url)
        WebDriverWait(driver, SELENIUM_WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
        time.sleep(PAGE_LOAD_SLEEP)
        html = driver.page_source
        logging.info(f"Successfully fetched content from {url}")
        return html
    except TimeoutException:
        logging.warning(f"Timeout waiting for page elements at {url}")
        return None
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return None


def quit_driver(driver):
    if driver:
        logging.info("Quitting WebDriver...")
        driver.quit()
        logging.info("WebDriver quit successfully.")
