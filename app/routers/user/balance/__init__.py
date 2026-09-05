from aiogram import Router

from app.routers.user.balance.common import common
from app.routers.user.balance.crypto_bot import crypto_bot
from app.routers.user.balance.sbp import sbp
from app.routers.user.balance.stars import stars

balance = Router()
balance.include_router(common)
balance.include_router(crypto_bot)
balance.include_router(stars)
balance.include_router(sbp)
