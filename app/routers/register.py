from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.database.queries.filters_queries import mark_user_subscribed, mark_user_unsubscribed
from app.database.queries.user_queries import new_registration
from app.filters.common import IsNotSubscribed, IsSubscribed
from app.keyboards import inline as kb
from app.utils.is_sub import is_subscribed
from app.utils.menu import show_main_menu

register = Router()
register.message.filter(IsNotSubscribed())
register.callback_query.filter(IsNotSubscribed())


@register.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id

    await new_registration(user_id)

    subscribed = await is_subscribed(message.bot, user_id)

    if subscribed:
        await mark_user_subscribed(user_id)
        await show_main_menu(message, user_id)
    else:
        await mark_user_unsubscribed(user_id)
        await message.answer(
            "Перед началом подпишитесь на наш канал:",
            reply_markup=kb.check_subscription_keyboard,
        )


@register.callback_query(F.data == "check_subscription")
async def callback_check(callback: CallbackQuery):
    subscribed = await is_subscribed(callback.bot, callback.from_user.id)

    if subscribed:
        await mark_user_subscribed(callback.from_user.id)
        await callback.message.answer("✅ Вы подписаны")
    else:
        await callback.message.answer("❌ Вы не подписаны")

    await callback.answer()
