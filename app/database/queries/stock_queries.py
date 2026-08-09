import aiosqlite

from app.database.init import DB_PATH


async def get_auto_quantity_stock(product_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT COUNT(*) FROM digital_stock WHERE product_id = (?) AND is_sold = 0",
            (product_id,),
        )

        row = await cursor.fetchone()
        return row[0]


async def get_manual_quantity_stock(product_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT COUNT(*) FROM manual_stock WHERE product_id = (?)",
            (product_id,),
        )

        row = await cursor.fetchone()
        return row[0]


async def get_digital_stock_content(product_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            """
            UPDATE digital_stock
            SET is_sold = 1
            WHERE id = (
                SELECT id FROM digital_stock
                WHERE product_id = ? AND is_sold = 0
                LIMIT 1
            )
            RETURNING content, id
            """,
            (product_id,),
        )
        row = await cursor.fetchone()
        await conn.commit()

        if row is None:
            return None

        return {
            "content": row[0],
            "id": row[1],
        }


async def set_order_id(id, order_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE digital_stock SET order_id = ? WHERE id = ?",
            (order_id, id),
        )
        await conn.commit()
