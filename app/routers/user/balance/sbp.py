from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, Message

import app.keyboards.inline as kb
from app.database.queries.payments import update_payment_method
from app.enums import PaymentMethod

sbp = Router()


@sbp.callback_query(F.data == "sbp_selection")
async def process_sbp(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Loading...")

    data = await state.get_data()
    payment_id = data["payment_id"]

    await update_payment_method(payment_id, PaymentMethod.SBP)

    if isinstance(callback.message, Message):
        await callback.message.edit_caption(
            caption="Сбпь",
            reply_markup=kb.cancel_payment,
        )

    elif isinstance(callback.message, InaccessibleMessage):
        # TODO: вывести ошибку про InaccessibleMessage через logger
        return

    else:
        # TODO: вывести ошибку через logger
        return
