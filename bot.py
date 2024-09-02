import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.methods import DeleteWebhook
from logging.handlers import RotatingFileHandler

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from common.bot_command_list import private
from database.engine import create_db, session_maker
from handlers.user_privat import user_privat_router
from handlers.admin_privat import admin_privat_router
from middlewares.db_middle import DataBaseSession

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

admin_privat_router.message.middleware(DataBaseSession(session_pool=session_maker))

dp.include_router(user_privat_router)
dp.include_router(admin_privat_router)

async def on_startup():
    await create_db()
    logging.info(' ############### Создана (подключение) база даннах. ############')

async def on_shutdown():
    logging.info(" ############### Бот закончил работать. ############")

async def run_bot():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    await bot(DeleteWebhook(drop_pending_updates=True))
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

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



