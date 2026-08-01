import aiosqlite

from app.database.init import DB_PATH


async def get_balance(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT balance FROM user_info WHERE user_id = ?",
            (user_id,),
        )

        row = await cursor.fetchone()
        return row[0]


async def top_up_balance(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE user_info SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id),
        )
        await conn.commit()


async def deduct_balance(user_id: int, amount: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "UPDATE user_info SET balance = balance - ? WHERE user_id = ? AND balance >= ?",
            (amount, user_id, amount),
        )
        await conn.commit()

        return cursor.rowcount > 0
