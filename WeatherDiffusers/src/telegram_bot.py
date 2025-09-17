from __future__ import annotations

import asyncio
import os
import logging
from typing import Optional

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

from src.service import generate_weather_image_for_city
from src.config import get_env as cfg_get_env, reload_env

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("telegram_bot")


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	await update.message.reply_text("Hi! Send /weather <city> to get a weather image.")


async def weather_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	args = context.args or []
	if not args:
		await update.message.reply_text("Usage: /weather <city name>")
		return
	city = " ".join(args)
	logger.info("/weather requested: %s (chat=%s)", city, update.effective_chat.id if update.effective_chat else None)
	try:
		await update.message.chat.send_action(action="upload_photo")
		path, msg = generate_weather_image_for_city(city)
		with open(path, "rb") as f:
			await update.message.reply_photo(photo=f, caption=msg)
		logger.info("Sent image: %s", path)
	except Exception as e:
		logger.exception("Failed to generate/send image: %s", e)
		await update.message.reply_text(f"Failed to generate weather image: {e}")


def run_bot() -> None:
	reload_env()
	token = cfg_get_env("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
	if not token:
		raise RuntimeError("TELEGRAM_BOT_TOKEN not set in environment or .env")
	app = Application.builder().token(token).build()
	app.add_handler(CommandHandler("start", start_handler))
	app.add_handler(CommandHandler("weather", weather_handler))
	logger.info("Starting polling...")
	app.run_polling(close_loop=False, allowed_updates=Update.ALL_TYPES, drop_pending_updates=True, poll_interval=1.0, bootstrap_retries=3)


if __name__ == "__main__":
	run_bot()
