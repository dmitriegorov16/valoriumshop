from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import text

from app.config import settings
from app.database.queries.category import get_categories
from app.database.queries.user import get_account_type
from app.enums import AccountType

check_subscription_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=f"{settings.CHANNEL_NAME}", url=f"https://t.me/{settings.CHANNEL_USERNAME}")],
        [InlineKeyboardButton(text="Проверить подписку", callback_data="check_subscription")],
    ],
)


check_subscription_keyboard_new = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=f"{settings.CHANNEL_NAME}", url=f"https://t.me/{settings.CHANNEL_USERNAME}")],
        [InlineKeyboardButton(text="Я подписался", callback_data="new_check_subscription")],
    ],
)


async def main_menu_keyboard(user_id: int):
    account_type = await get_account_type(user_id)

    if account_type == AccountType.ADMIN:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Каталог", callback_data="catalog"),
                    InlineKeyboardButton(text="Профиль", callback_data="profile"),
                ],
                [InlineKeyboardButton(text="Поддержка", callback_data="support")],
                [InlineKeyboardButton(text="Админ панель", callback_data="admin_panel")],
            ]
        )

    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Каталог", callback_data="catalog"),
                    InlineKeyboardButton(text="Профиль", callback_data="profile"),
                ],
                [InlineKeyboardButton(text="Поддержка", callback_data="support")],
            ]
        )


# функция нужна для будущего (например колво юзеров)
async def admin_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пользователи", callback_data="admin_users")],
            [
                InlineKeyboardButton(text="Статистика", callback_data="admin_stat"),
                InlineKeyboardButton(text="Рассылка", callback_data="admin_rassilka"),
            ],
            [InlineKeyboardButton(text="Категории и товары", callback_data="admin_catalog")],
            [InlineKeyboardButton(text="Финансы", callback_data="admin_momey")],
            [InlineKeyboardButton(text="Назад", callback_data="back_main")],
        ]
    )


async def admin_catalog_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    categories = await get_categories()

    if not categories:
        keyboard.add(InlineKeyboardButton(text="Пока категорий нету"))
    else:
        for category in categories or []:
            keyboard.add(InlineKeyboardButton(text=category["name"], callback_data=f"admin_category_{category['id']}"))

    keyboard.row(InlineKeyboardButton(text="Создать категорию", callback_data="create_category"))
    keyboard.row(InlineKeyboardButton(text="Назад", callback_data="admin_panel"))

    return keyboard.as_markup()


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

accept_offer_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Принять", callback_data="accept_offer")],
    ]
)
