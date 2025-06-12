from db import get_products, save_products, get_subscriptions, save_subscriptions
from telegram import Bot
import asyncio
import os
import time

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN)

def notify_and_update_products():
    async def notify_loop():
        while True:
            subs = get_subscriptions()
            for sub in subs:
                user_id = sub["user_id"]
                alias = sub["alias"]
                pincode = sub.get("pincode")
                if not pincode:
                    print(f"Subscription for user {user_id} missing pincode, skipping.")
                    continue
                products = get_products(pincode=pincode)
                product = next((p for p in products if p.get("alias") == alias), None)
                if not product:
                    print(f"No product found for alias {alias} in pincode {pincode}.")
                    continue
                now_qty = product.get("inventory_quantity", 0)
                new_status = "in_stock" if now_qty > 0 else "out_of_stock"
                last_status = sub.get("last_notified_status", None)
                if last_status != new_status:
                    try:
                        if new_status == "in_stock":
                            await bot.send_message(
                                chat_id=user_id,
                                text=f"{product['name']} is back in stock! (₹{product['price']})\n{product['url']}"
                            )
                        else:
                            await bot.send_message(
                                chat_id=user_id,
                                text=f"{product['name']} is now OUT OF STOCK. We'll notify you when it's back!"
                            )
                    except Exception as e:
                        print(f"Failed to notify {user_id}: {e}")
                    sub["last_notified_status"] = new_status
            print(f"Sent status updates for all subscriptions.")
            await asyncio.sleep(420)  # 7 minutes
    asyncio.run(notify_loop())

if __name__ == "__main__":
    notify_and_update_products()
