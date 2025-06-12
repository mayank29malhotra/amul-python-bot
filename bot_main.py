from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from db import get_products, get_subscriptions, save_subscriptions
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Amul Product Notifier!\nUse /products to see available products."
    )

async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = get_products()
    if not products:
        await update.message.reply_text("No products found. Please try again later.")
        return
    # Telegram requires callback_data to be max 64 bytes and only valid UTF-8
    # We'll use only the alias, and ensure it's a string and not too long
    buttons = [
        [InlineKeyboardButton(f"{p['name']} (₹{p['price']})", callback_data=p['alias'][:60])]
        for p in products
    ]
    await update.message.reply_text(
        "Select a product to subscribe:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    alias = query.data
    products = get_products()
    product = next((p for p in products if p["alias"][:60] == alias), None)
    if not product:
        await query.edit_message_text("Product not found.")
        return
    user_id = query.from_user.id
    subs = get_subscriptions()
    # Remove any existing sub for this user (user can only have one subscription)
    subs = [s for s in subs if s["user_id"] != user_id]
    # Add new subscription with last_notified_status
    last_status = "in_stock" if product.get("inventory_quantity", 0) > 0 else "out_of_stock"
    subs.append({
        "user_id": user_id,
        "alias": product["alias"],
        "name": product["name"],
        "last_notified_status": last_status
    })
    save_subscriptions(subs)
    # Notify user about product availability
    if product.get("inventory_quantity", 0) > 0:
        msg = f"Subscribed to {product['name']}!\n\nThis product is currently IN STOCK."
    else:
        msg = f"Subscribed to {product['name']}!\n\nThis product is currently NOT AVAILABLE."
    await query.edit_message_text(msg)

application = Application.builder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("products", products))
application.add_handler(CallbackQueryHandler(button))

if __name__ == "__main__":
    application.run_polling()
