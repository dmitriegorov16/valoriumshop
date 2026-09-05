from aiogram import Router

from app.routers.user.balance import balance
from app.routers.user.catalog import catalog
from app.routers.user.products import product
from app.routers.user.profile import profile
from app.routers.user.start import start
from app.routers.user.utils import sync_subscription_status

user = Router()
user.include_router(start)
user.include_router(profile)
user.include_router(balance)
user.include_router(catalog)
user.include_router(product)
