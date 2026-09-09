from aiogram import Router

from app.routers.admin.catalog import catalog
from app.routers.admin.menu import menu

admin = Router()
admin.include_router(menu)
admin.include_router(catalog)
