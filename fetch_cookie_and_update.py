# fetch_cookie_and_update.py
"""
This script uses Selenium to fetch a fresh cookie and API URL from the Amul website and writes them to api_url_and_headers.json.
Run this script every 2 hours (e.g., on Replit or your local machine).
"""
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os

GITHUB_TOKEN = os.environ.get("TOKEN_GITHUB")
GIST_ID = os.environ.get("GIST_ID")
GIST_FILENAME = os.environ.get("GIST_FILENAME", "api_url_and_headers.json")


def update_gist(content):
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "files": {
            GIST_FILENAME: {
                "content": content
            }
        }
    }
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Gist updated successfully.")
    else:
        print(f"Failed to update Gist: {response.status_code} {response.text}")

def fetch_cookie_and_url():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    try:
        driver.get('https://shop.amul.com/en/browse/protein')
        time.sleep(5)  # Wait for page to load and cookies to be set
        cookies = driver.get_cookies()
        cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
        api_url = (
            "https://shop.amul.com/api/1/entity/ms.products"
            "?fields[name]=1&fields[brand]=1&fields[categories]=1&fields[collections]=1"
            "&fields[alias]=1&fields[sku]=1&fields[price]=1&fields[compare_price]=1"
            "&fields[original_price]=1&fields[images]=1&fields[metafields]=1&fields[discounts]=1"
            "&fields[catalog_only]=1&fields[is_catalog]=1&fields[seller]=1&fields[available]=1"
            "&fields[inventory_quantity]=1&fields[net_quantity]=1&fields[num_reviews]=1"
            "&fields[avg_rating]=1&fields[inventory_low_stock_quantity]=1"
            "&fields[inventory_allow_out_of_stock]=1&fields[default_variant]=1&fields[variants]=1"
            "&fields[lp_seller_ids]=1&facets=true&facetgroup=default_category_facet"
            "&filters[0][field]=categories&filters[0][value][0]=protein&filters[0][operator]=in"
            "&filters[0][original]=1&limit=24&total=1&start=0&cdc=1m&substore=66505ff5145c16635e6cc74d"
        )
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "base_url": "https://shop.amul.com/en/browse/protein",
            "cookie": cookie_str,
            "frontend": "1",
            "priority": "u=1, i",
            "referer": "https://shop.amul.com/",
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": driver.execute_script("return navigator.userAgent;")
        }
        json_content = json.dumps({"API_URL": api_url, "HEADERS": headers}, ensure_ascii=False, indent=2)
        update_gist(json_content)
        print("Updated Gist with fresh cookie and headers.")
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_cookie_and_url()
