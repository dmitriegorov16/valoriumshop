import logging

import aiosqlite

from app.database.init import DB_PATH
from app.types.categories import Category

logger = logging.getLogger(__name__)


async def get_categories() -> list[Category]:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT category_id, category_name FROM categories WHERE parent_id IS NULL"
        )
        rows = await cursor.fetchall()

        categories = []
        for row in rows:
            categories.append(
                {
                    "id": row[0],
                    "name": row[1],
                }
            )

        return categories


async def get_subcategories(parent_id) -> list[Category]:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT category_id, category_name FROM categories WHERE parent_id = ?",
            (parent_id,),
        )

        rows = await cursor.fetchall()

        subcategories = []
        for row in rows:
            subcategories.append(
                {
                    "id": row[0],
                    "name": row[1],
                }
            )

        return subcategories


async def get_category_name(category_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT category_name FROM categories WHERE category_id = ?",
            (category_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            logger.warning("Категория с id=%s не найдена", category_id)
            return None
        return row[0]


async def get_category_parent_id(category_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT parent_id FROM categories WHERE category_id = ?",
            (category_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            logger.warning("Категория с id=%s не найдена", category_id)
            return None
        return row[0]


async def get_category_photo(category_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT image FROM categories WHERE category_id = ?",
            (category_id,),
        )

        row = await cursor.fetchone()
        if row is None:
            logger.info("Фото категории с id=%s не найдена", category_id)
            return None
        return row[0]
