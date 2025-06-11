import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler

# Telegram credentials (set directly or use environment variables)
TELEGRAM_TOKEN = "8133480794:AAGWMhio0K6W08dydB1fY6UDd5UN-yVvvRo"
TELEGRAM_CHAT_ID = "1692585982"

# Use the Amul API endpoint for product data
AMUL_API_URL = "https://shop.amul.com/api/1/entity/ms.products?fields[name]=1&fields[brand]=1&fields[categories]=1&fields[collections]=1&fields[alias]=1&fields[sku]=1&fields[price]=1&fields[compare_price]=1&fields[original_price]=1&fields[images]=1&fields[metafields]=1&fields[discounts]=1&fields[catalog_only]=1&fields[is_catalog]=1&fields[seller]=1&fields[available]=1&fields[inventory_quantity]=1&fields[net_quantity]=1&fields[num_reviews]=1&fields[avg_rating]=1&fields[inventory_low_stock_quantity]=1&fields[inventory_allow_out_of_stock]=1&fields[default_variant]=1&fields[variants]=1&fields[lp_seller_ids]=1&filters[0][field]=categories&filters[0][value][0]=protein&filters[0][operator]=in&filters[0][original]=1&facets=true&facetgroup=default_category_facet&limit=24&total=1&start=0&cdc=1m&substore=66505ff5145c16635e6cc74d"

bot = Bot(token=TELEGRAM_TOKEN)


def fetch_amul_products():
    """Fetch Amul product data from the Amul API (replicates amul-backend logic)."""
    response = requests.get(AMUL_API_URL)
    response.raise_for_status()
    data = response.json()
    products = data.get("data", [])
    # Return a list of dicts with key info
    return [
        {
            "name": p.get("name"),
            "alias": p.get("alias"),
            "price": p.get("price"),
            "inventory_quantity": p.get("inventory_quantity"),
            "url": f'https://shop.amul.com/en/product/{p.get("alias")}'
        }
        for p in products
    ]


def send_telegram_notification(message):
    """Send a message to the Telegram chat."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def job():
    products = fetch_amul_products()
    in_stock = [p for p in products if p["inventory_quantity"] and p["inventory_quantity"] > 0]
    if in_stock:
        message = 'Amul Products In Stock:\n' + '\n'.join([
            f"{p['name']} (₹{p['price']}) - {p['inventory_quantity']} in stock\n{p['url']}" for p in in_stock
        ])
        send_telegram_notification(message)
    else:
        send_telegram_notification('No Amul products are currently in stock.')


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    # Run every day at 9:00 AM (customize as needed)
    scheduler.add_job(job, 'cron', hour=9, minute=0)
    print('Amul product tracker bot started.')
    scheduler.start()
