import requests
import json
from db import save_products
import os
import time

def get_api_url_and_headers():
    try:        # Use your actual Gist raw URL
        url = os.environ.get("GIST_URL")
        resp = requests.get(url, timeout=10)
        data = resp.json()
        print("Loaded API_URL and HEADERS from Gist successfully.")
        return data["API_URL"], data["HEADERS"]
    except Exception as e:
        print(f"Failed to load API_URL and HEADERS from Gist: {e}")
        # Provide fallback static values if Gist fetch fails
        fallback_api_url = (
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
        fallback_headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "base_url": "https://shop.amul.com/en/browse/protein",
            "cookie": "",
            "frontend": "1",
            "priority": "u=1, i",
            "referer": "https://shop.amul.com/",
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        }
        return fallback_api_url, fallback_headers


def refresh_headers():
    while True:
        try:
            return get_api_url_and_headers()
        except Exception as e:
            print(f"Header refresh failed: {e}. Retrying in 2 minutes...")
            time.sleep(120)

def fetch_and_save_products():
    API_URL, HEADERS = refresh_headers()
    while True:
        try:
            response = requests.get(API_URL, headers=HEADERS)
            if response.status_code != 200:
                print(f"Failed to fetch products: {response.status_code} {response.text}")
                time.sleep(60)
                API_URL, HEADERS = refresh_headers()
                continue
            data = response.json()
        except Exception as e:
            print(f"Failed to fetch or parse JSON: {e}\nResponse text: {getattr(response, 'text', '')}")
            time.sleep(60)
            API_URL, HEADERS = refresh_headers()
            continue
        # Save full API response for debugging
        with open("api_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        products = data.get("data", [])
        product_list = [
            {
                "name": p.get("name"),
                "alias": p.get("alias"),
                "url": f'https://shop.amul.com/en/product/{p.get("alias")}',
                "price": p.get("price"),
                "compare_price": p.get("compare_price"),
                "inventory_quantity": p.get("inventory_quantity"),
                "available": p.get("available"),
                "image": p.get("images", [{}])[0].get("image") if p.get("images") else None,
                "categories": p.get("categories"),
                "collections": p.get("collections"),
                "benefits": p.get("metafields", {}).get("benefits") if p.get("metafields") else None,
                "description": p.get("description"),
            }
            for p in products
        ]
        save_products(product_list)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Updated {len(product_list)} products.")
        # Refresh headers for next run
        API_URL, HEADERS = refresh_headers()
        time.sleep(6000)  # 1 hour 40 minutes

if __name__ == "__main__":
    fetch_and_save_products()