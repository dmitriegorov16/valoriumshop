from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InaccessibleMessage, Message

from app.database.queries.olds.filters_queries import mark_user_subscribed, mark_user_unsubscribed
from app.database.queries.user import new_registration
from app.filters.common import IsNotSubscribed
from app.keyboards import inline as kb
from app.utils.is_sub import is_subscribed
from app.utils.menu import show_main_menu

register = Router()
register.message.filter(IsNotSubscribed())
register.callback_query.filter(IsNotSubscribed())


@register.message(CommandStart())
async def cmd_start(message: Message):
    from_user = message.from_user
    if from_user is None:
        # TODO: вывести ошибку через logger
        return

    user_id = from_user.id

    await new_registration(user_id)

    bot = message.bot

    if bot is None:
        # TODO: вывести ошибку через logger
        return

    subscribed = await is_subscribed(bot, user_id)

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
    bot = callback.bot
    if bot is None:
        # TODO: вывести ошибку через logger
        return

    subscribed = await is_subscribed(bot, callback.from_user.id)

    if isinstance(callback.message, Message):
        if subscribed:
            await callback.answer()
            await mark_user_subscribed(callback.from_user.id)
            await callback.message.answer("✅ Вы подписаны")
        else:
            await callback.answer()
            await callback.message.answer("❌ Вы не подписаны")

    elif isinstance(callback.message, InaccessibleMessage):
        # TODO: вывести ошибку про InaccessibleMessage через logger
        return

    else:
        # TODO: вывести ошибку через logger
        return
