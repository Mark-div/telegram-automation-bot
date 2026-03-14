import logging
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from bot.config import settings
from bot.database import init_db, save_message, get_user_stats
from bot.scheduler import setup_scheduler

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        f"Hi <b>{user.first_name}</b>! 👋\n\n"
        f"I'm your automation assistant. Here's what I can do:\n\n"
        f"/stats — your usage statistics\n"
        f"/schedule — manage scheduled tasks\n"
        f"/help — show this message"
    )
    logger.info(f"New user: {user.id} ({user.username})")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = await get_user_stats(user_id)
    await update.message.reply_text(
        f"📊 Your stats:\n\n"
        f"Messages sent: {data['total_messages']}\n"
        f"Member since: {data['first_seen']}\n"
        f"Last active: {data['last_active']}"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n"
        "/start — welcome message\n"
        "/stats — your statistics\n"
        "/schedule — scheduled tasks\n"
        "/help — this message"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    await save_message(
        user_id=user.id,
        username=user.username or "",
        text=text,
        timestamp=datetime.utcnow(),
    )

    await update.message.reply_text(f"Got it! You said: {text}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling update: {context.error}", exc_info=context.error)


def create_app() -> Application:
    app = Application.builder().token(settings.TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    return app


async def main():
    await init_db()
    app = create_app()
    setup_scheduler(app)

    logger.info("Bot starting...")
    await app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    asyncio.run(main())
