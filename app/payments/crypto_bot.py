import logging
import math
import os

from aiosend import TESTNET, CryptoPay
from dotenv import load_dotenv

load_dotenv()
cp = CryptoPay(os.getenv("CRYPTO_PAY_TOKEN"), TESTNET)

logger = logging.getLogger(__name__)


def round_up(value: float, decimals: int = 2) -> float:
    factor = 10**decimals
    return math.ceil(value * factor) / factor


async def rub_to_usdt(amount_rub) -> float:
    amount_usdt = await cp.exchange(amount_rub, "RUB", "USDT")
    return round_up(amount_usdt, 2)


# TODO: добавить настройку url бота
async def create_crypto_bot_invoice(amount_rub, payment_id, message):
    try:
        invoice_link = await cp.create_invoice(
            amount=await rub_to_usdt(amount_rub),
            asset="USDT",
            description=f"Пополнение баланса на {amount_rub} руб",
            swap_to="USDT",
            hidden_message="Успешное пополнение баланса",
            paid_btn_name="openBot",
            paid_btn_url="https://t.me/dmitri_shop_bot",
            payload=str(payment_id),
        )
    except Exception:
        logger.exception(
            "Ошибка создания инвойса CryptoBot: payment_id=%s, amount=%s руб",
            payment_id,
            amount_rub,
        )
        raise

    logger.info(
        "Создан инвойс CryptoBot invoice_id=%s: payment_id=%s, amount=%s руб",
        invoice_link.invoice_id,
        payment_id,
        amount_rub,
    )

    # без .poll() клиент не отслеживает статус инвойса, и invoice_paid не сработает
    invoice_link.poll(message=message)

    return invoice_link.bot_invoice_url
