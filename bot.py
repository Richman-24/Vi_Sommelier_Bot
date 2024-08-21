import os
import sys
import asyncio
import logging

from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook

from dotenv import load_dotenv
load_dotenv()

from handlers.user_privat import user_privat_router

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

dp.include_router(user_privat_router)

async def run_bot():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
     
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler("vi_som_bot.log", encoding="UTF-8", maxBytes=1000000, backupCount=5),
            logging.StreamHandler(sys.stdout)
        ]
    )
    asyncio.run(run_bot())

