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
            products = get_products()
            subs = get_subscriptions()
            for product in products:
                name = product.get("name")
                alias = product.get("alias")
                now_qty = product.get("inventory_quantity", 0)
                low_stock_qty = product.get("inventory_low_stock_quantity", 0)
                # Determine new status using low stock threshold
                new_status = "in_stock" if now_qty > low_stock_qty else "out_of_stock"
                for sub in subs:
                    if sub["alias"] == alias:
                        user_id = sub["user_id"]
                        last_status = sub.get("last_notified_status", None)
                        # try:
                        #     if new_status == "in_stock":
                        #         await bot.send_message(
                        #             chat_id=user_id,
                        #             text=f"{product['name']} is back in stock! (₹{product['price']})\n{product['url']}"
                        #         )
                        #     else:
                        #         await bot.send_message(
                        #             chat_id=user_id,
                        #             text=f"{product['name']} is now OUT OF STOCK. We'll notify you when it's back!"
                        #         )
                        # except Exception as e:
                        #     print(f"Failed to notify {user_id}: {e}")
                        # sub["last_notified_status"] = new_status
                    
                                            
                        # Notify if status changed
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
            print(f"Sent status updates for {len(products)} protein products to all subscribers.")
            await asyncio.sleep(300)  # 5 minutes
    asyncio.run(notify_loop())

if __name__ == "__main__":
    notify_and_update_products()
