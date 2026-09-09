from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.keyboards.inline import admin_catalog_keyboard

catalog = Router()


@catalog.callback_query(F.data == "admin_catalog")
async def catalog_menu(callback: CallbackQuery):
    if callback.message and isinstance(callback.message, Message):
        keyboard = await admin_catalog_keyboard()

        if not keyboard:
            print("нету")
            return

        await callback.message.edit_caption(
            caption="Категории и товары",
            reply_markup=keyboard,
        )
