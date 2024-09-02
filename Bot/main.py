import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from gas_fee_fetcher import GasFeeFetcher
from user_preferences import UserPreferences
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Initialize bot, gas fee fetcher, and user preferences
TOKEN = os.getenv('7256965214:AAG3uK88GNpx17yubxSM9ODJOX-Hyr9P9fE')
gas_fetcher = GasFeeFetcher()
user_prefs = UserPreferences()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcome to the Gas Fee Alert Bot! Use /set_chains to choose chains for alerts.')

async def set_chains(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Ethereum", callback_data='chain_ethereum'),
         InlineKeyboardButton("Binance Smart Chain", callback_data='chain_binance'),
         InlineKeyboardButton("Polygon", callback_data='chain_binance'),
         InlineKeyboardButton("Tron", callback_data='chain_binance'),
         InlineKeyboardButton("Arbitrum", callback_data='chain_binance'),
         InlineKeyboardButton("Solana", callback_data='chain_binance'),
         InlineKeyboardButton("Optimism", callback_data='chain_binance')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Select chains for gas fee alerts:', reply_markup=reply_markup)

async def chain_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    chain = query.data.split('_')[1]

    user_chains = user_prefs.get_user_chains(user_id)
    if chain in user_chains:
        user_chains.remove(chain)
    else:
        user_chains.append(chain)

    user_prefs.set_user_chains(user_id, user_chains)
    await query.edit_message_text(f"You've selected: {', '.join(user_chains)}")

async def set_threshold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.split()
    if len(text) != 3:
        await update.message.reply_text("Usage: /set_threshold <chain> <threshold_in_usd>")
        return

    chain = text[1]
    threshold = float(text[2])
    user_prefs.set_user_threshold(user_id, chain, threshold)
    await update.message.reply_text(f"Threshold for {chain} set to ${threshold}")

async def check_gas_fees(context: ContextTypes.DEFAULT_TYPE):
    while True:
        for user_id, prefs in user_prefs.preferences.items():
            for chain in prefs.get('chains', []):
                gas_fee = gas_fetcher.fetch_gas_fee(chain)
                threshold = user_prefs.get_user_threshold(user_id, chain)
                if gas_fee and threshold and gas_fee < threshold:
                    await context.bot.send_message(chat_id=user_id, text=f"Gas fee alert for {chain}: ${gas_fee}")
        await asyncio.sleep(300)  # Check every 5 minutes

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_chains", set_chains))
    application.add_handler(CallbackQueryHandler(chain_callback))
    application.add_handler(CommandHandler("set_threshold", set_threshold))

    asyncio.create_task(check_gas_fees(application))

    application.run_polling()

if __name__ == '__main__':
    main()