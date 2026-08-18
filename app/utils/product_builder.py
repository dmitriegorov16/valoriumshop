from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.types.products import ProductType


def products_builder(products: list[ProductType], back_callback: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for product in products:
        keyboard.add(InlineKeyboardButton(text=product["name"], callback_data=f"product_{product['id']}"))

    keyboard.adjust(2)
    keyboard.row(InlineKeyboardButton(text="Назад", callback_data=back_callback))
    return keyboard.as_markup()


def product_builder(product_id: int, back_callback: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Купить", callback_data=f"buy_{product_id}"))
    keyboard.row(InlineKeyboardButton(text="Назад", callback_data=back_callback))
    return keyboard.as_markup()
