import math
import os

from aiogram import Bot
from aiogram.types import LabeledPrice
from dotenv import load_dotenv

load_dotenv()
EXCHANGE_RATE = float(os.getenv("STARS_EXCHANGE_RATE"))


def rub_to_stars(amount_rub) -> int:
    amount_stars = amount_rub * EXCHANGE_RATE
    return math.ceil(amount_stars)


async def create_stars_invoice_link(bot: Bot, payment_id, amount_rub):
    invoice_link = await bot.create_invoice_link(
        title="Пополнение баланса",
        description=f"Пополнение баланса на {amount_rub} руб",
        payload=str(payment_id),
        currency="XTR",
        prices=[LabeledPrice(label=f"Пополнение на {amount_rub} руб", amount=rub_to_stars(amount_rub))],
    )

    return invoice_link
