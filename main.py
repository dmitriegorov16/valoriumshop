import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.database.init import init_db
from app.routers.register import register
from app.routers.user import user


# TODO: добавить логи
async def main():
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    dp = Dispatcher()
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    dp.include_routers(user, register)
    await dp.start_polling(bot)


async def startup(dispatcher: Dispatcher):
    await init_db()


async def shutdown(dispatcher: Dispatcher):
    pass


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
