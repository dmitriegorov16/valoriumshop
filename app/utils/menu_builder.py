from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.types.categories import CategoryType


def menu_builder(categories: list[CategoryType], back_callback: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(text=category["name"], callback_data=f"category_{category['id']}"))

    keyboard.adjust(2)
    keyboard.row(InlineKeyboardButton(text="Назад", callback_data=back_callback))
    return keyboard.as_markup()
