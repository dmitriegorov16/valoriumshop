import logging

import aiosqlite

from app.database.init import DB_PATH

logger = logging.getLogger(__name__)


async def new_registration(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "INSERT OR IGNORE INTO user_info(user_id) VALUES (?)",
            (user_id,),
        )
        await conn.commit()

        if cursor.rowcount > 0:
            logger.info("Новый пользователь зарегистрирован: user_id=%s", user_id)
            return True
        else:
            logger.debug("Пользователь user_id=%s уже зарегистрирован", user_id)
            return False


async def get_registered_at(user_id: int) -> str | None:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT registered_at FROM user_info WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()

        if row is None:
            logger.warning("Пользователь user_id=%s не найден", user_id)
            return None

        return row[0]


async def get_account_type(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT account_type FROM user_info WHERE user_id = ?",
            (user_id,),
        )

        row = await cursor.fetchone()

        if row is None:
            logger.warning("Пользователь user_id=%s не найден", user_id)
            return None

        return row[0]
