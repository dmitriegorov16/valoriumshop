import aiosqlite

from app.database.init import DB_PATH


async def mark_user_subscribed(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE user_info SET is_sub = TRUE WHERE user_id = ?",
            (user_id,),
        )
        await conn.commit()


async def mark_user_unsubscribed(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE user_info SET is_sub = FALSE WHERE user_id = ?",
            (user_id,),
        )
        await conn.commit()


async def is_user_subscribed(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT is_sub FROM user_info WHERE user_id = ?",
            (user_id,),
        )

        row = await cursor.fetchone()
        return bool(row[0]) if row else False
