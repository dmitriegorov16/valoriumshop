from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InaccessibleMessage, InputMediaPhoto, Message

import app.keyboards.inline as kb
from app.database.queries.payments import create_payment
from app.states import PaymentStates

common = Router()


@common.callback_query(F.data == "top_up")
async def top_up(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Loading...")
    top_up_photo = FSInputFile("images/system/topup.png")

    if isinstance(callback.message, Message):
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=top_up_photo,
                caption="Введите сумму пополнения в рублях (минимум 50 руб)",
            ),
            reply_markup=kb.back_profile_keyboard,
        )
        await state.update_data(
            bot_message_id=callback.message.message_id,
            bot_chat_id=callback.message.chat.id,
        )
        await state.set_state(PaymentStates.amount)

    elif isinstance(callback.message, InaccessibleMessage):
        # TODO: вывести ошибку про InaccessibleMessage через logger
        return

    else:
        # TODO: вывести ошибку через logger
        return


@common.message(PaymentStates.amount)
async def process_amount(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    if not message.text or not message.text.isdigit():
        try:
            await bot.edit_message_caption(
                chat_id=data["bot_chat_id"],
                message_id=data["bot_message_id"],
                caption="Пожалуйста, введите число",
                reply_markup=kb.back_profile_keyboard,
            )
        except TelegramBadRequest:
            pass
        await message.delete()
        return

    amount = int(message.text)
    if amount < 50:
        try:
            await bot.edit_message_caption(
                chat_id=data["bot_chat_id"],
                message_id=data["bot_message_id"],
                caption="Минимальная сумма — 50 руб",
                reply_markup=kb.back_profile_keyboard,
            )
        except TelegramBadRequest:
            pass
        await message.delete()
        return

    from_user = message.from_user

    if from_user is None:
        # TODO: ошибка через logger
        return

    user_id = from_user.id
    payment_id = await create_payment(user_id, amount)
    await state.update_data(payment_id=payment_id)
    await state.set_state(None)

    data = await state.get_data()
    await bot.edit_message_caption(
        chat_id=data["bot_chat_id"],
        message_id=data["bot_message_id"],
        caption=f"Пополнение на {amount} р\nВыберете метод оплаты",
        reply_markup=kb.selection_method,
    )

    await message.delete()
