from sqlalchemy import select

from app.database.engine import async_session
from app.database.models import Category
from app.types.categories import CategoryType


async def get_categories() -> list[CategoryType] | None:
    async with async_session() as session:
        result = await session.execute(
            select(Category).where(Category.parent_id == None),
        )

        categories = result.scalars().all()
        if not categories:
            return None

        return [
            CategoryType(
                id=category.category_id,
                name=category.category_name,
                parent_id=category.parent_id,
                photo=category.image,
            )
            for category in categories
        ]


async def get_subcategories(parent_id: int) -> list[CategoryType] | None:
    async with async_session() as session:
        result = await session.execute(
            select(Category).where(Category.parent_id == parent_id),
        )

        categories = result.scalars().all()
        if not categories:
            return None

        return [
            CategoryType(
                id=category.category_id,
                name=category.category_name,
                parent_id=category.parent_id,
                photo=category.image,
            )
            for category in categories
        ]


async def get_category_name(category_id: int) -> str | None:
    async with async_session() as session:
        check_result = await session.execute(
            select(Category).where(Category.category_id == category_id),
        )

        existing = check_result.scalar_one_or_none()

        if not existing:
            return None

        result = await session.execute(select(Category.category_name).where(Category.category_id == category_id))

        category_name = result.scalar_one()
        return category_name


async def get_category_parent_id(category_id: int) -> int | None:
    async with async_session() as session:
        result = await session.execute(
            select(Category.parent_id).where(Category.category_id == category_id),
        )

        parent_id = result.scalar_one_or_none()
        return parent_id


async def get_category_photo(category_id: int) -> str | None:
    async with async_session() as session:
        result = await session.execute(
            select(Category.image).where(Category.category_id == category_id),
        )

        category_photo = result.scalar_one_or_none()
        return category_photo


async def get_category_serial_number(serial_number: int) -> int | None:
    async with async_session() as session:
        result = await session.execute(
            select(Category.serial_number).where(Category.serial_number == serial_number),
        )

        result = result.scalar_one_or_none()
        return result


# TODO: мб сделать так что если в бд вместо фото флаг например "not_photo" то он будет брать
# вышестоящее фото а если и его нет то дефолтное фото


async def create_new_category(
    name: str, serial_number: int, parent_id: int | None = None, image: str | None = None
) -> CategoryType:
    async with async_session() as session:
        category = Category(
            category_name=name,
            serial_number=serial_number,
            parent_id=parent_id,
            image=image,
        )

        session.add(category)
        await session.commit()


        return CategoryType(
            id=category.category_id,
            name=category.category_name,
            parent_id=category.parent_id,
            photo=category.image,
        )
