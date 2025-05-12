import csv
import logging
import os
from typing import List, Dict, Any


def initialize_csv(file_path: str, fieldnames: List[str]):
    try:
        write_header = not os.path.exists(file_path) or os.path.getsize(file_path) == 0
        with open(
            file_path, "w" if write_header else "a", newline="", encoding="utf-8"
        ) as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
                logging.info(f"CSV header written to {file_path}")
            else:
                logging.info(f"CSV file {file_path} already exists. Appending.")
    except IOError as e:
        logging.error(f"Error initializing CSV file {file_path}: {e}")
        raise


def append_to_csv(file_path: str, fieldnames: List[str], data_dict: Dict[str, Any]):
    try:
        with open(file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writerow(data_dict)
    except IOError as e:
        logging.error(
            f"Error writing row to CSV {file_path} for product {data_dict.get('product_title', 'N/A')}: {e}"
        )
    except Exception as e:
        logging.error(
            f"Unexpected error writing row to CSV {file_path} for product {data_dict.get('product_title', 'N/A')}: {e}"
        )
