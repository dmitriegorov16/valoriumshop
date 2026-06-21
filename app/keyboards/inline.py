import os

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

load_dotenv()
CHANNEL_NAME = os.getenv("CHANNEL_NAME")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

check_subscription_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=f"{CHANNEL_NAME}", url=f"https://t.me/{CHANNEL_USERNAME}")],
        [InlineKeyboardButton(text="Проверить подписку", callback_data="check_subscription")],
    ]
)


main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Каталог", callback_data="catalog"),
            InlineKeyboardButton(text="Профиль", callback_data="profile"),
        ],
        [InlineKeyboardButton(text="Поддержка", callback_data="support")],
    ]
)
