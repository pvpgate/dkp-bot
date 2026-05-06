import asyncio
import os

from aiogram import Bot, Dispatcher
from database.db import init_db
from handlers import routers

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

bot = Bot(token=TOKEN)
dp = Dispatcher()

for r in routers:
    dp.include_router(r)


async def main():
    await init_db()   # ✅ ВАЖНО: await

    print("BOT STARTED")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())