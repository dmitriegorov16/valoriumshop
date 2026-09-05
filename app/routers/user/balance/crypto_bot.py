import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, Message
from aiosend.types import Invoice

import app.keyboards.inline as kb
from app.database.queries.balance import top_up_balance
from app.database.queries.payments import get_amount, mark_payment_paid, update_payment_method
from app.enums import PaymentMethod
from app.payments.crypto_bot import cp, create_crypto_bot_invoice

logger = logging.getLogger(__name__)
crypto_bot = Router()


@crypto_bot.callback_query(F.data == "crypto_bot_selection")
async def process_crypto_bot(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Loading...")

    data = await state.get_data()
    payment_id = data["payment_id"]

    await update_payment_method(payment_id, PaymentMethod.CRYPTO_BOT)
    amount = await get_amount(payment_id)

    payment_link = await create_crypto_bot_invoice(
        amount,
        payment_id,
        callback.message,
    )
    if isinstance(callback.message, Message):
        await callback.message.edit_caption(
            caption=f"Оплата {amount} руб",
            reply_markup=kb.create_crypto_bot_payment(payment_link),
        )

    elif isinstance(callback.message, InaccessibleMessage):
        # TODO: вывести ошибку про InaccessibleMessage через logger
        return

    else:
        # TODO: вывести ошибку через logger
        return


@cp.invoice_paid()
async def handle_payment(invoice: Invoice, message: Message):
    if invoice.payload is None:
        # TODO: обработать ошибку через logger
        return

    payment_id = int(invoice.payload)
    charge_id = str(invoice.invoice_id)

    from_user = message.from_user

    if from_user is None:
        # TODO: обработать ошибку через logger
        return

    user_id = from_user.id

    if not await mark_payment_paid(payment_id, charge_id):
        # платёж уже был обработан ранее (повторный вебхук) либо payment_id некорректен —
        # баланс НЕ трогаем, чтобы не начислить его дважды
        logger.warning("Повторная или некорректная обработка оплаты payment_id=%s", payment_id)
        return

    amount = int(await get_amount(payment_id))
    await top_up_balance(user_id, amount)
    logger.info(
        "Зачислена оплата CryptoBot: payment_id=%s, user_id=%s, amount=%s руб, invoice_id=%s",
        payment_id,
        user_id,
        amount,
        charge_id,
    )
    await message.answer("Оплата прошла успешно! ✅")
