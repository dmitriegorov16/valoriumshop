import logging
import math
import os

from aiogram import Bot
from aiogram.types import LabeledPrice
from dotenv import load_dotenv

load_dotenv()
exchange_rate = os.getenv("STARS_EXCHANGE_RATE")
if exchange_rate is None:
    raise

EXCHANGE_RATE = float(exchange_rate)

logger = logging.getLogger(__name__)


def rub_to_stars(amount_rub) -> int:
    amount_stars = amount_rub * EXCHANGE_RATE
    return math.ceil(amount_stars)


async def create_stars_invoice_link(bot: Bot, payment_id, amount_rub):
    amount_stars = rub_to_stars(amount_rub)

    try:
        invoice_link = await bot.create_invoice_link(
            title="Пополнение баланса",
            description=f"Пополнение баланса на {amount_rub} руб",
            payload=str(payment_id),
            currency="XTR",
            prices=[LabeledPrice(label=f"Пополнение на {amount_rub} руб", amount=amount_stars)],
        )
    except Exception:
        logger.exception(
            "Ошибка создания Stars-инвойса: payment_id=%s, amount=%s руб (%s stars)",
            payment_id,
            amount_rub,
            amount_stars,
        )
        raise

    logger.info(
        "Создан Stars-инвойс: payment_id=%s, amount=%s руб (%s stars)",
        payment_id,
        amount_rub,
        amount_stars,
    )

    return invoice_link
