import aiosqlite

from app.database.init import DB_PATH
from app.types.products import Product


async def get_products(category_id) -> list[Product]:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT product_id, category_id, name, description, price FROM products WHERE category_id = ? AND in_stock = TRUE",
            (category_id,),
        )
        rows = await cursor.fetchall()

        products = []
        for row in rows:
            products.append(
                {
                    "id": row[0],
                    "category_id": row[1],
                    "name": row[2],
                    "description": row[3],
                    "price": row[4],
                }
            )

        return products


async def get_product(product_id) -> Product:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT product_id, category_id, name, description, price FROM products WHERE product_id = ?",
            (product_id,),
        )

        row = await cursor.fetchone()

        return {
            "id": row[0],
            "category_id": row[1],
            "name": row[2],
            "description": row[3],
            "price": row[4],
        }


async def get_product_photo(product_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT image FROM products WHERE product_id = ?",
            (product_id,),
        )

        row = await cursor.fetchone()
        return row[0]


async def get_delivery_type(product_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT delivery_type FROM products WHERE product_id = ?",
            (product_id,),
        )

        row = await cursor.fetchone()
        return row[0]


async def set_out_of_stock(product_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE products SET in_stock = FALSE WHERE product_id = ?",
            (product_id),
        )
        await conn.commit()
