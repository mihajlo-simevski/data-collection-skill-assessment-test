# Data Collection - Skill Assessment Test

## Installing Python 3.13

- pip3 install requests beautifulsoup4 lxml

## Plan

- Scrap 500 products

- Scrap 1 product
- Identify selectors
- Extract data
- Structure data
- Handle errors

- Expand code for more URLs

Refine and adjust


### Identifying selectors

- main_image: item-image
- seller_name: item-brand (title)
- product_rating: item-rating
- product_final_price: price-current (currency, integer_part(strong), fraction_part(sup))
- product_description: item-features (list of li items)
- product_title: item-title