# File-based JSON storage utility
import json
import os
from threading import Lock

PRODUCTS_FILE = os.getenv("PRODUCTS_FILE", "products.json")
SUBSCRIPTIONS_FILE = os.getenv("SUBSCRIPTIONS_FILE", "subscriptions.json")

products_lock = Lock()
subs_lock = Lock()

def get_products():
    with products_lock:
        if not os.path.exists(PRODUCTS_FILE):
            return []
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

def save_products(products):
    with products_lock:
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

def get_subscriptions():
    with subs_lock:
        if not os.path.exists(SUBSCRIPTIONS_FILE):
            return []
        with open(SUBSCRIPTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

def save_subscriptions(subs):
    with subs_lock:
        with open(SUBSCRIPTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(subs, f, ensure_ascii=False, indent=2)

def save_products_from_api_response():
    with open("api_response.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    products = data.get("data", [])
    with products_lock:
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as pf:
            json.dump(products, pf, ensure_ascii=False, indent=2)
