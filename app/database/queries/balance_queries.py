import logging

import aiosqlite

from app.database.init import DB_PATH

logger = logging.getLogger(__name__)


async def get_balance(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT balance FROM user_info WHERE user_id = ?",
            (user_id,),
        )

        row = await cursor.fetchone()
        logger.info("Получен баланс пользователя %s: %s руб", user_id, row[0])
        return row[0]


async def top_up_balance(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE user_info SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id),
        )
        await conn.commit()
        logger.info("Баланс пользователя %s пополнен на %s руб", user_id, amount)


async def deduct_balance(user_id: int, amount: int) -> bool:
    if amount <= 0:
        logger.warning("Некорректная сумма списания %s для пользователя %s", amount, user_id)
        return False

    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "UPDATE user_info SET balance = balance - ? WHERE user_id = ? AND balance >= ?",
            (amount, user_id, amount),
        )
        await conn.commit()

        result = cursor.rowcount

        if result > 0:
            logger.info("Баланс пользователя %s успешно уменьшен на %s", user_id, amount)
            return True
        else:
            logger.info("Баланс пользователя %s не был уменьшен на %s", user_id, amount)
            return False
