import logging

import aiosqlite

from app.database.init import DB_PATH

logger = logging.getLogger(__name__)


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


async def get_digital_stock_content(product_id: int) -> dict | None:
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
            logger.warning("Нет доступного товара в наличии для product_id=%s", product_id)
            return None

        logger.info("Выдан товар со склада: stock_id=%s, product_id=%s", row[1], product_id)

        return {
            "content": row[0],
            "id": row[1],
        }


async def set_order_id(id: int, order_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "UPDATE digital_stock SET order_id = ? WHERE id = ?",
            (order_id, id),
        )
        await conn.commit()

        if cursor.rowcount > 0:
            logger.info("У записи склада id=%s установлен order_id=%s", id, order_id)
            return True
        else:
            logger.warning("Не удалось установить order_id=%s: запись склада id=%s не найдена", order_id, id)
            return False
