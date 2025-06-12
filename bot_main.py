from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from db import get_products, get_subscriptions, save_subscriptions
import os
import json

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

# Temporary dict to track users awaiting pincode input
pending_pincode = {}

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
    # Ask for pincode
    pending_pincode[user_id] = product
    await query.edit_message_text(f"You selected: {product['name']}\nPlease enter your delivery pincode:")

# Load supported pincodes at startup
with open("pincodes.txt", "r", encoding="utf-8") as f:
    SUPPORTED_PINCODES = set(line.strip() for line in f if line.strip().isdigit() and len(line.strip()) == 6)

async def handle_pincode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in pending_pincode:
        return  # Ignore messages not expecting pincode
    pincode = update.message.text.strip()
    if not pincode.isdigit() or len(pincode) != 6:
        await update.message.reply_text("Please enter a valid 6-digit pincode:")
        return
    if pincode not in SUPPORTED_PINCODES:
        await update.message.reply_text("Your pincode is not supported for tracking yet.")
        return
    product = pending_pincode.pop(user_id)
    subs = get_subscriptions()
    # Remove any existing sub for this user
    subs = [s for s in subs if s["user_id"] != user_id]
    last_status = "in_stock" if product.get("inventory_quantity", 0) > 0 else "out_of_stock"
    subs.append({
        "user_id": user_id,
        "alias": product["alias"],
        "name": product["name"],
        "pincode": pincode,
        "last_notified_status": last_status
    })
    save_subscriptions(subs)
    if product.get("inventory_quantity", 0) > 0:
        msg = f"Subscribed to {product['name']} for pincode {pincode}!\n\nThis product is currently IN STOCK."
    else:
        msg = f"Subscribed to {product['name']} for pincode {pincode}!\n\nThis product is currently NOT AVAILABLE."
    await update.message.reply_text(msg)

application = Application.builder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("products", products))
application.add_handler(CallbackQueryHandler(button))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_pincode))

if __name__ == "__main__":
    application.run_polling()
