import aiosqlite

from app.database.init import DB_PATH


async def create_order(user_id, product_id, delivery_type, price, status="pending"):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "INSERT INTO orders (user_id, product_id, delivery_type, price, status) VALUES (?, ?, ?, ?, ?)",
            (user_id, product_id, delivery_type, price, status),
        )
        await conn.commit()
        return cursor.lastrowid
