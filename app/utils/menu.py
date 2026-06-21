from aiogram.types import Message

from app.keyboards import inline as kb


async def show_main_menu(message: Message):
    await message.answer("главное меню типа", reply_markup=kb.main_menu_keyboard)
