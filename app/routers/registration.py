from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, InaccessibleMessage, Message, User

import app.keyboards.inline as kb
from app.database.queries.filters import mark_user_subscribed
from app.database.queries.offer import create_agreement
from app.database.queries.user import new_registration
from app.utils.is_sub import is_subscribed
from app.utils.menu import _edit_main_menu, _show_main_menu

registration = Router()


async def _start_registration(message: Message, bot: Bot):
    """start registration"""
    if isinstance(message.from_user, User):
        user = message.from_user

    is_sub = await is_subscribed(bot=bot, user_id=user.id)

    if is_sub:
        await _prompt_offer_accept(message, edit=False)

    else:
        await message.answer(text="Подпишитесь на канал", reply_markup=kb.check_subscription_keyboard_new)


async def _prompt_offer_accept(message: Message, edit: bool = True):
    # TODO: замена на систему текста в файлах
    text = "Оферта ValoriumShop\n-----------------\n1. делать контебуты\n2. не воровать"

    if edit:
        await message.edit_text(text, reply_markup=kb.accept_offer_keyboard)
    else:
        await message.answer(text, reply_markup=kb.accept_offer_keyboard)


async def _complete_registration(message: Message, user_id: int):
    await new_registration(user_id=user_id)
    await mark_user_subscribed(user_id=user_id)
    await _edit_main_menu(message, user_id)


@registration.callback_query(F.data == "new_check_subscription")
async def check_subscription(callback: CallbackQuery):
    bot = callback.bot
    if bot is None:
        # TODO: вывести ошибку через logger
        return

    subscribed = await is_subscribed(bot, callback.from_user.id)

    if isinstance(callback.message, Message):
        if subscribed:
            print("подписан")
            await callback.answer("✅ Вы подписаны")
            await _prompt_offer_accept(callback.message)

        else:
            print("не подписан")
            await callback.answer("❌ Вы не подписаны", show_alert=True)

    elif isinstance(callback.message, InaccessibleMessage):
        # TODO: вывести ошибку про InaccessibleMessage через logger
        return

    else:
        # TODO: вывести ошибку через logger
        return


@registration.callback_query(F.data == "accept_offer")
async def process_offer_accept(callback: CallbackQuery):
    await create_agreement(callback.from_user.id)
    if isinstance(callback.message, Message):
        await _complete_registration(callback.message, callback.from_user.id)
