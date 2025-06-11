import requests
import json
from db import save_products
import os
import time

API_URL = (
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

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "base_url": "https://shop.amul.com/en/browse/protein",
    "cookie": "jsessionid=s%3AruRx8ymTK58ext75zepkZGIZ.aIhW0VIm5Gk9dEvJ%2BcuW3isceaEH36ZeDb0YwuL8glw; _ga=GA1.1.111495461.1749539254; __cf_bm=M_hJgCXygFEX0hqICph3h53eRhrw_opidhqtBTZunvU-1749618924-1.0.1.1-F4Zazg1wWuN9umOV_BIExPvAgDeSONXstuU2UIpirOBNLvSCSkBtdaW1sU.v3no4RNwF2sGmBUfp2HfkwKpwhNO52wEI3KqHy17oHyY5Dd8; _ga_E69VZ8HPCN=GS2.1.s1749618926$o4$g0$t1749618936$j50$l0$h1434577086",
    "frontend": "1",
    "priority": "u=1, i",
    "referer": "https://shop.amul.com/",
    "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "tid": "1749618935698:220:4b8477eb3ce4e8dc6401d185b018e75687aaec89db30a02c20ee59e949e90cb5",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
}

def fetch_and_save_products():
    while True:
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
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
        print(f"Updated {len(product_list)} products.")
        # Wait 5 minutes (300 seconds) before next update
        time.sleep(300)

if __name__ == "__main__":
    fetch_and_save_products()