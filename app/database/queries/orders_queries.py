import aiosqlite

from app.database.init import DB_PATH


async def create_order(user_id, product_id, delivery_type, price):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "INSERT INTO orders (user_id, product_id, delivery_type, price) VALUES (?, ?, ?, ?)",
            (user_id, product_id, delivery_type, price),
        )
        await conn.commit()
        return cursor.lastrowid
