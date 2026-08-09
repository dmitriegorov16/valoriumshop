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
    ],
)


main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Каталог", callback_data="catalog"),
            InlineKeyboardButton(text="Профиль", callback_data="profile"),
        ],
        [InlineKeyboardButton(text="Поддержка", callback_data="support")],
    ],
)


profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Пополнить", callback_data="top_up")],
        [InlineKeyboardButton(text="Рефералы", callback_data="referrals")],
        [InlineKeyboardButton(text="Назад", callback_data="back_main")],
    ]
)


back_main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_main")],
    ]
)

back_profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="profile")],
    ]
)


selection_method = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="СБП", callback_data="sbp_selection")],
        [InlineKeyboardButton(text="Крипто Бот", callback_data="crypto_bot_selection")],
        [InlineKeyboardButton(text="Звезды", callback_data="stars_selection")],
        [InlineKeyboardButton(text="Назад", callback_data="top_up")],
    ]
)


cancel_payment = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отмена", callback_data="profile")],
    ]
)


def create_stars_payment(payment_link: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить ⭐️", url=payment_link)],
            [InlineKeyboardButton(text="Отмена", callback_data="profile")],
        ]
    )


def create_crypto_bot_payment(payment_link: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить 🤖", url=payment_link)],
            [InlineKeyboardButton(text="Отмена", callback_data="profile")],
        ]
    )


not_money = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Пополнить", callback_data="top_up")],
        [InlineKeyboardButton(text="Назад", callback_data="back_main")],
    ],
)
