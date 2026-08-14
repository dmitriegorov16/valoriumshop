import logging

import aiosqlite

from app.database.init import DB_PATH
from app.types.payment import Payment

logger = logging.getLogger(__name__)


async def create_payment(user_id: int, amount: int) -> int:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "INSERT INTO payments (user_id, amount, status) VALUES (?, ?, 'draft')",
            (user_id, amount),
        )

        await conn.commit()
        logger.info(
            "Создан платёж id=%s: user_id=%s, amount=%s, status=draft", cursor.lastrowid, user_id, amount
        )
        return cursor.lastrowid


async def get_payment(payment_id: int) -> Payment:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT id, user_id, amount, method, status, external_id, created_at FROM payments WHERE id = ?",
            (payment_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            logger.warning("Платёж id=%s не найден", payment_id)
            return None
        return Payment(
            id=row[0],
            user_id=row[1],
            amount=row[2],
            method=row[3],
            status=row[4],
            external_id=row[5],
            created_at=row[6],
        )


async def update_payment_method(payment_id: int, method: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "UPDATE payments SET method = ? WHERE id = ?",
            (method, payment_id),
        )
        await conn.commit()

        if cursor.rowcount > 0:
            logger.info("Платежу id=%s установлен метод оплаты %s", payment_id, method)
        else:
            logger.warning(
                "Не удалось установить метод оплаты %s: платёж id=%s не найден", method, payment_id
            )


async def mark_payment_paid(payment_id: int, external_id: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "UPDATE payments SET status = 'paid', external_id = ? WHERE id = ?",
            (external_id, payment_id),
        )
        await conn.commit()

        if cursor.rowcount > 0:
            logger.info(
                "Платёж id=%s помечен как оплаченный, external_id=%s",
                payment_id,
                external_id,
            )
            return True
        else:
            logger.error(
                "Не удалось пометить платёж id=%s как оплаченный: платёж не найден, external_id=%s",
                payment_id,
                external_id,
            )
            return False


async def get_amount(payment_id: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT amount FROM payments WHERE id = ?",
            (payment_id,),
        )

        row = await cursor.fetchone()
        return row[0]
