from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.routers.admin.utils import _edit_admin_menu

menu = Router()


@menu.callback_query(F.data == "admin_panel")
async def admin_menu(callback: CallbackQuery):
    if callback.message and isinstance(callback.message, Message):
        await _edit_admin_menu(callback.message)
