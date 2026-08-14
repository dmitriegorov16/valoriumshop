import logging

import aiosqlite

from app.database.init import DB_PATH

logger = logging.getLogger(__name__)


async def mark_user_subscribed(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "UPDATE user_info SET is_sub = TRUE WHERE user_id = ?",
            (user_id,),
        )
        await conn.commit()

        if cursor.rowcount > 0:
            logger.info("Пользователь user_id=%s отмечен как подписанный", user_id)
        else:
            logger.warning(
                "Не удалось отметить подписку: пользователь user_id=%s не найден", user_id
            )


async def mark_user_unsubscribed(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "UPDATE user_info SET is_sub = FALSE WHERE user_id = ?",
            (user_id,),
        )
        await conn.commit()

        if cursor.rowcount > 0:
            logger.info("Пользователь user_id=%s отмечен как отписавшийся", user_id)
        else:
            logger.warning(
                "Не удалось снять подписку: пользователь user_id=%s не найден", user_id
            )


async def is_user_subscribed(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT is_sub FROM user_info WHERE user_id = ?",
            (user_id,),
        )

        row = await cursor.fetchone()
        return bool(row[0]) if row else False
