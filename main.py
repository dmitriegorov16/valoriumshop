import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.database.init import init_db
from app.payments.crypto_bot import cp
from app.routers.register import register
from app.routers.user import user

# _levelToName = {
#     CRITICAL: 'CRITICAL',
#     ERROR: 'ERROR',
#     WARNING: 'WARNING',
#     INFO: 'INFO',
#     DEBUG: 'DEBUG',
#     NOTSET: 'NOTSET',
# }

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    dp = Dispatcher()
    logger.info("Диспетчер инициализирован")
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    dp.include_routers(user, register)

    tasks = [
        asyncio.create_task(dp.start_polling(bot)),
        asyncio.create_task(cp.start_polling()),
    ]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
    await asyncio.gather(*pending, return_exceptions=True)
    for task in done:
        task.result()


async def startup(dispatcher: Dispatcher):
    await init_db()


async def shutdown(dispatcher: Dispatcher):
    logger.info("Бот выключен")


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
