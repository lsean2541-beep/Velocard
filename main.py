import os
import random
import asyncio
import logging
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock holder names repository
MOCK_NAMES = [
    "ALEXANDER WRIGHT", "SOPHIA CHEN", "LIAM O'CONNOR", "AMARA OKORO", 
    "MATEO RODRIGUEZ", "ELENA PETROVA", "YUKI TANAKA", "DAVID MILLER"
]

# Luhn Algorithm Checksum Generator to ensure realistic card formatting
def complete_luhn(partial_num: str) -> str:
    digits = [int(x) for x in partial_num]
    odd_sum = sum(digits[-1::-2])
    even_sum = sum([sum(divmod(2 * d, 10)) for d in digits[-2::-2]])
    checksum = (10 - ((odd_sum + even_sum) % 10)) % 10
    return partial_num + str(checksum)

def generate_mock_card(card_type: str) -> dict:
    # Set prefixes and structural rules based on network standard layouts
    if card_type == "visa":
        prefix = "4" + "".join(random.choice("0123456789") for _ in range(14))
        full_number = complete_luhn(prefix)
        formatted_num = " ".join([full_number[i:i+4] for i in range(0, 16, 4)])
        cvv = str(random.randint(100, 999))
    elif card_type == "mastercard":
        prefix = str(random.choice([51, 52, 53, 54, 55])) + "".join(random.choice("0123456789") for _ in range(13))
        full_number = complete_luhn(prefix)
        formatted_num = " ".join([full_number[i:i+4] for i in range(0, 16, 4)])
        cvv = str(random.randint(100, 999))
    else:  # amex
        prefix = str(random.choice([34, 37])) + "".join(random.choice("0123456789") for _ in range(12))
        full_number = complete_luhn(prefix)
        # Amex format is 4-6-5 digits spacing
        formatted_num = f"{full_number[0:4]} {full_number[4:10]} {full_number[10:15]}"
        cvv = str(random.randint(1000, 9999)) # Amex uses 4-digit CID/CVV

    # Generate expiry date window (2 to 5 years into the future)
    future_months = random.randint(24, 60)
    expiry_date = datetime.now() + timedelta(days=future_months * 30)
    expiry_str = expiry_date.strftime("%m/%y")
    
    return {
        "number": formatted_num,
        "holder": random.choice(MOCK_NAMES),
        "expiry": expiry_str,
        "cvv": cvv
    }

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💳 Visa Mockup", callback_data="gen_visa")],
        [InlineKeyboardButton("💳 Mastercard Mockup", callback_data="gen_mastercard")],
        [InlineKeyboardButton("💳 American Express Mockup", callback_data="gen_amex")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = (
        "⚡ **Welcome to VeloCard!** ⚡\n\n"
        "Generate cryptographically compliant mockup virtual cards for interface layouts, "
        "checkout system trials, and data processing tests.\n\n"
        "👇 **Select a network standard below to generate a card matrix:**"
    )
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode="Markdown")

# Handle Generation Request Buttons
async def handle_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    card_type = query.data.split("_")[1]
    card_data = generate_mock_card(card_type)
    
    network_title = card_type.upper()
    emoji = "🔵" if card_type == "visa" else "🔴" if card_type == "mastercard" else "⚫"
    
    response_msg = (
        f"{emoji} **{network_title} VIRTUAL CARD MOCKUP**\n"
        f"⚠️ _For System Testing & Interface Mockups Only_\n\n"
        f"💳 **Card Number:** `{card_data['number']}`\n"
        f"📅 **Expiry Date:** `{card_data['expiry']}`\n"
        f"🔒 **CVV / CID:** `{card_data['cvv']}`\n"
        f"👤 **Card Holder:** `{card_data['holder']}`\n\n"
        f"💡 _Tap on individual metrics above to quickly copy values on mobile._"
    )
    
    # Render option panel below results to cycle generation configurations
    keyboard = [
        [InlineKeyboardButton("🔄 Generate Another Card", callback_data=query.data)],
        [InlineKeyboardButton("🏠 Back to Network Menu", callback_data="back_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(response_msg, reply_markup=reply_markup, parse_mode="Markdown")

# Back to main landing index configuration state
async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("💳 Visa Mockup", callback_data="gen_visa")],
        [InlineKeyboardButton("💳 Mastercard Mockup", callback_data="gen_mastercard")],
        [InlineKeyboardButton("💳 American Express Mockup", callback_data="gen_amex")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = (
        "⚡ **VeloCard Generator Main Menu** ⚡\n\n"
        "👇 **Select a network standard below to generate a card matrix:**"
    )
    await query.message.edit_text(msg, reply_markup=reply_markup, parse_mode="Markdown")

def main():
    # Explicit loop initialization logic ensuring full Python 3.14.3 Render environment compatibility
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if not TOKEN:
        logger.error("No BOT_TOKEN found in environment config!")
        return

    application = Application.builder().token(TOKEN).build()

    # Handlers Configuration Map
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_back, pattern="^back_menu$"))
    application.add_handler(CallbackQueryHandler(handle_generation, pattern="^gen_"))

    print("🤖 VeloCard dummy network engine active and processing pipelines loaded...")
    application.run_polling()

if __name__ == "__main__":
    main()
