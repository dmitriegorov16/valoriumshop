import aiosqlite

from app.database.init import DB_PATH


async def get_auto_quantity_stock(product_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT COUNT(*) FROM digital_stock WHERE product_id = (?) AND is_sold = 0",
            (product_id,),
        )

        row = await cursor.fetchall()
        return row[0]


async def get_manual_quantity_stock(product_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT COUNT(*) FROM manual_stock WHERE product_id = (?)",
            (product_id,),
        )

        row = await cursor.fetchall()
        return row[0]
