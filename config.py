BASE_URL = "https://www.newegg.com"
STARTING_CATEGORY_URL = (
    "https://www.newegg.com/Headphones-Accessories/SubCategory/ID-70?PageSize=96"
)
MAX_PRODUCTS_TO_SCRAPE = 500
CSV_FILE_NAME = "headphone_products.csv"
CSV_FIELDNAMES = [
    "product_title",
    "product_description",
    "product_price",
    "product_rating",
    "seller_name",
    "main_image_url",
]

HEADLESS_BROWSER = True
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)
WINDOW_SIZE = "1920,1080"
SELENIUM_WAIT_TIMEOUT = 10
PAGE_LOAD_SLEEP = 2

PRODUCT_LINK_SELECTOR = "div.item-container a.item-title"
NEXT_PAGE_LINK_SELECTOR = 'a[title="Next"]'

PRODUCT_TITLE_SELECTOR = "h1.product-title"
PRODUCT_PRICE_SELECTOR = "div.price-current"
PRODUCT_PRICE_DOLLARS_SELECTOR = "div.price-current strong"
PRODUCT_PRICE_CENTS_SELECTOR = "div.price-current sup"
PRODUCT_SELLER_SELECTOR = "div.product-seller-sold-by strong"
PRODUCT_DESCRIPTION_BULLETS_SELECTOR = "div.product-bullets ul li"
PRODUCT_RATING_SELECTOR = "div.product-rating i.rating"
PRODUCT_IMAGE_SELECTOR = "img.product-view-img-original"
