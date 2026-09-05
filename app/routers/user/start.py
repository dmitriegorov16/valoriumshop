from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

import app.keyboards.inline as kb
from app.routers.registration import _start_registration
from app.routers.user.utils import _edit_main_menu, _show_main_menu, sync_subscription_status

start = Router()


@start.message(CommandStart())
async def cmd_start(message: Message, is_new: bool, bot: Bot):
    from_user = message.from_user

    if from_user is None:
        # TODO: добавить обработку в logger
        return

    user_id = from_user.id
    if is_new:
        await _start_registration(message, bot)
    else:
        subscribed = await sync_subscription_status(bot, user_id)
        if subscribed:
            await _show_main_menu(message, user_id)
        else:
            await message.answer(text="Подпишитесь на канал", reply_markup=kb.check_subscription_keyboard)


@start.callback_query(F.data == "check_subscription")
async def process_check_subscription(callback: CallbackQuery):
    if callback.bot is None:
        # TODO: вывести ошибку через logger
        return

    subscribed = await sync_subscription_status(callback.bot, callback.from_user.id)

    if not isinstance(callback.message, Message):
        # TODO: вывести ошибку про InaccessibleMessage через logger
        return

    if subscribed:
        await callback.answer("✅ Вы подписаны")
        await callback.message.delete()
    else:
        await callback.answer("❌ Вы не подписаны", show_alert=True)


@start.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    message = callback.message

    if not isinstance(message, Message):
        # TODO: написать обработку ошибки
        return

    if callback.bot is None:
        # TODO: написать обработку ошибки
        return

    subscribed = await sync_subscription_status(callback.bot, user_id)

    if subscribed:
        await _edit_main_menu(message, user_id)
    else:
        await message.answer(
            "Перед началом подпишитесь на наш канал:",
            reply_markup=kb.check_subscription_keyboard,
        )
