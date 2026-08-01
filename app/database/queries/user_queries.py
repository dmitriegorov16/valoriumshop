import aiosqlite

from app.database.init import DB_PATH


async def new_registration(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT OR IGNORE INTO user_info(user_id) VALUES (?)",
            (user_id,),
        )
        await conn.commit()


async def get_registered_at(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT registered_at FROM user_info WHERE user_id = ?",
            (user_id,),
        )

        row = await cursor.fetchone()
        return row[0]
