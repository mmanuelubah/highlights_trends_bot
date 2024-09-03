import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import TOKEN
from gas_fetcher import fetch_gas_price
from price_fetcher import fetch_coin_price, COINGECKO_IDS
from user_preferences import UserPreferences
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

user_prefs = UserPreferences()
active_updates = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Ethereum", callback_data='ethereum'),
         InlineKeyboardButton("BNB Chain", callback_data='binancecoin')],
        [InlineKeyboardButton("Solana", callback_data='solana'),
         InlineKeyboardButton("Optimism", callback_data='optimism')],
        [InlineKeyboardButton("Arbitrum", callback_data='arbitrum'),
         InlineKeyboardButton("Polygon", callback_data='polygon')],
        [InlineKeyboardButton("Stop Updates", callback_data='stop_updates')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Select a chain to get continuous gas price updates in USD, or stop updates:', reply_markup=reply_markup)
    logger.info(f"Start command initiated by user {update.effective_user.id}")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    user_id = query.from_user.id
    chain = query.data

    if chain == 'stop_updates':
        await stop_updates(update, context)
        return

    if user_id in active_updates:
        active_updates[user_id]['active'] = False
        if 'update_task' in context.user_data:
            context.user_data['update_task'].cancel()

    active_updates[user_id] = {'chain': chain, 'active': True}

    await query.edit_message_text(f"Starting continuous updates for {chain.capitalize()}...")
    # Create the task and store it in the context
    context.user_data['update_task'] = asyncio.create_task(send_continuous_updates(context.bot, user_id, chain))
    logger.info(f"Continuous updates started for {chain} by user {user_id}")

async def send_continuous_updates(bot, user_id, chain):
    inactive_count = 0
    max_inactive_count = 5  # Stop after 5 minutes of inactivity

    while active_updates.get(user_id, {}).get('active', False):
        try:
            gas_price = await fetch_gas_price(chain)
            coin_price = await fetch_coin_price(COINGECKO_IDS[chain])

            if chain == 'solana':
                usd_price = gas_price * coin_price
                native_price = f"{gas_price:.5f} SOL"
            else:
                usd_price = (gas_price / 1e9) * coin_price  # Convert Gwei to full coin
                native_price = f"{gas_price:.2f} Gwei"

            threshold = user_prefs.get_alert(user_id, chain)

            if threshold is not None:
                if usd_price >= 5 * threshold:
                    emoji = "⚠️"
                elif usd_price <= threshold:
                    emoji = "✅"
                else:
                    emoji = "💡"
            else:
                emoji = "💡"

            message = f"{emoji} Gas price update for {chain.capitalize()}:\n"
            message += f"${usd_price:.2f} USD\n"
            message += f"({native_price})"

            if threshold is not None:
                message += f"\nYour alert threshold: ${threshold:.2f} USD"

            message += "\n\nDeveloped by mmanuelubah"

            await bot.send_message(chat_id=user_id, text=message)
            logger.info(f"Gas price update sent for {chain} to user {user_id}")

            # Wait for user interaction
            try:
                await bot.wait_for_chat_member(chat_id=user_id, user_id=user_id, timeout=60)
                inactive_count = 0  # Reset inactive count if user interacts
            except asyncio.TimeoutError:
                inactive_count += 1

            if inactive_count >= max_inactive_count:
                logger.info(f"User {user_id} inactive for {max_inactive_count} minutes. Stopping updates.")
                active_updates[user_id]['active'] = False
                await bot.send_message(chat_id=user_id, text="Updates stopped due to inactivity. Use /start to begin again.")
                break

        except Exception as e:
            logger.error(f"Error sending update for {chain} to user {user_id}: {str(e)}", exc_info=True)

        await asyncio.sleep(60)  # Wait for 1 minute before the next update

async def set_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    try:
        _, chain, threshold = update.message.text.split()
        threshold = float(threshold)
        user_prefs.set_alert(user_id, chain, threshold)
        await update.message.reply_text(f"Alert threshold set for {chain.capitalize()} at ${threshold:.2f} USD")
        logger.info(f"Alert threshold set for {chain} at ${threshold:.2f} USD by user {user_id}")
    except ValueError:
        error_message = "Invalid format. Use: /alert {chain} {usd_threshold}"
        await update.message.reply_text(error_message)
        logger.warning(f"Invalid alert format used by user {user_id}")

async def stop_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query:
        user_id = query.from_user.id
        message_func = query.edit_message_text
        await query.answer()
    else:
        user_id = update.effective_user.id
        message_func = update.message.reply_text

    if user_id in active_updates:
        active_updates[user_id]['active'] = False
        chain = active_updates[user_id]['chain']
        if 'update_task' in context.user_data:
            context.user_data['update_task'].cancel()
            del context.user_data['update_task']
        message = f"Stopped continuous updates for {chain.capitalize()}."
        await message_func(message)
        logger.info(f"Continuous updates stopped for {chain} by user {user_id}")
    else:
        message = "No active updates to stop."
        await message_func(message)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def run_bot_with_retry() -> None:
    application = (
        Application.builder()
        .token(TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("alert", set_alert))
    application.add_handler(CommandHandler("stop", stop_updates))

    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

def run_bot():
    try:
        run_bot_with_retry()
    except RetryError as e:
        logger.error(f"Failed to start the bot after multiple attempts: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    run_bot()