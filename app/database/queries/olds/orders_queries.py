import logging

import aiosqlite

from app.database.init import DB_PATH

logger = logging.getLogger(__name__)


async def create_order(user_id, product_id, delivery_type, price, status="pending"):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "INSERT INTO orders (user_id, product_id, delivery_type, price, status) VALUES (?, ?, ?, ?, ?)",
            (user_id, product_id, delivery_type, price, status),
        )
        logger.info(
            "Создан заказ user_id=%s, product_id=%s, price=%s, status=%s",
            user_id,
            product_id,
            price,
            status,
        )
        await conn.commit()
        return cursor.lastrowid
