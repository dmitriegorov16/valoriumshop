import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, Message, PreCheckoutQuery

import app.keyboards.inline as kb
from app.database.queries.balance import top_up_balance
from app.database.queries.payments import get_amount, get_payment, mark_payment_paid, update_payment_method
from app.enums import PaymentMethod
from app.payments.stars import create_stars_invoice_link

logger = logging.getLogger(__name__)
stars = Router()


@stars.callback_query(F.data == "stars_selection")
async def process_stars(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer("Loading...")

    data = await state.get_data()
    payment_id = data["payment_id"]

    await update_payment_method(payment_id, PaymentMethod.STARS)
    amount = await get_amount(payment_id)

    payment_link = await create_stars_invoice_link(
        bot,
        payment_id,
        amount,
    )
    if isinstance(callback.message, Message):
        await callback.message.edit_caption(
            caption=f"Оплата {amount} руб",
            reply_markup=kb.create_stars_payment(payment_link),
        )

    elif isinstance(callback.message, InaccessibleMessage):
        # TODO: вывести ошибку про InaccessibleMessage через logger
        return

    else:
        # TODO: вывести ошибку через logger
        return


@stars.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    payment_id = int(pre_checkout_query.invoice_payload)
    payment = await get_payment(payment_id)

    if payment is None or payment["status"] == "paid":
        logger.warning(
            "Отклонён pre_checkout: payment_id=%s, user_id=%s, status=%s",
            payment_id,
            pre_checkout_query.from_user.id,
            payment["status"] if payment else "not_found",
        )
        await pre_checkout_query.answer(
            ok=False,
            error_message="Платёж недоступен, попробуйте создать новый.",
        )
        return

    await pre_checkout_query.answer(ok=True)


@stars.message(F.successful_payment)
async def process_successful_payment(message: Message, bot: Bot):
    from_user = message.from_user

    if not from_user:
        # TODO: написать обработку ошибки
        return

    payment = message.successful_payment

    if not payment:
        # TODO: написать обработку ошибки
        return

    payment_id = int(payment.invoice_payload)
    telegram_charge_id = payment.telegram_payment_charge_id
    user_id = from_user.id

    if not await mark_payment_paid(payment_id, telegram_charge_id):
        logger.warning("Повторная или некорректная обработка оплаты payment_id=%s", payment_id)
        return

    amount = int(await get_amount(payment_id))
    await top_up_balance(user_id, amount)
    logger.info(
        "Зачислена оплата Stars: payment_id=%s, user_id=%s, amount=%s руб, charge_id=%s",
        payment_id,
        user_id,
        amount,
        telegram_charge_id,
    )
    await message.answer("Оплата прошла успешно! ✅")
