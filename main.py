import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiosend import CryptoPay

from app.config import settings
from app.database.engine import init_db
from app.middlewares.access import AccessMiddleware
from app.middlewares.errors import ErrorHandlingMiddleware
from app.middlewares.identity import IdentityMiddleware
from app.middlewares.throttling import ThrottlingMiddleware
from app.payments.crypto_bot import cp
from app.routers.registration import registration
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
    bot = Bot(settings.TELEGRAM_TOKEN)
    dp = Dispatcher()
    logger.info("Диспетчер инициализирован")
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    dp.include_routers(user, registration)
    access_middleware = AccessMiddleware()
    identity_middleware = IdentityMiddleware()
    error_handling_middleware = ErrorHandlingMiddleware()
    throttling_middleware = ThrottlingMiddleware()

    dp.message.outer_middleware(error_handling_middleware)
    dp.callback_query.outer_middleware(error_handling_middleware)
    dp.message.middleware(throttling_middleware)
    dp.callback_query.middleware(throttling_middleware)
    dp.message.outer_middleware(identity_middleware)
    dp.callback_query.outer_middleware(identity_middleware)
    dp.message.outer_middleware(access_middleware)
    dp.callback_query.outer_middleware(access_middleware)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(dp.start_polling(bot, handle_signals=False))
        tg.create_task(_poll_crypto_bot())


async def _poll_crypto_bot() -> None:
    await cp.start_polling()


async def startup(dispatcher: Dispatcher):
    await init_db()


async def shutdown(dispatcher: Dispatcher):
    logger.info("Бот выключен")


if __name__ == "__main__":
    asyncio.run(main())
