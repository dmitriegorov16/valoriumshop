from sqlalchemy import delete, func, select, update

from app.database.engine import async_session
from app.database.models import DigitalStock


async def get_auto_quantity_stock(product_id: int) -> int:
    async with async_session() as session:
        result = await session.execute(
            select(func.count())
            .select_from(DigitalStock)
            .where(
                DigitalStock.product_id == product_id,
                DigitalStock.is_sold.is_(False),
            )
        )

        return result.scalar_one()


async def get_digital_stock_content(product_id) -> dict:
    async with async_session() as session:
        query = (
            select(DigitalStock.id)
            .where(DigitalStock.product_id == product_id, DigitalStock.is_sold == False)
            .limit(1)
        )

        result = await session.execute(
            update(DigitalStock)
            .where(DigitalStock.id == query.scalar_subquery())
            .values(is_sold=True)
            .returning(DigitalStock),
        )

        stock = result.scalar_one_or_none()
        await session.commit()

        return {
            "content": stock.content,
            "id": stock.id,
        }


async def set_order_id(id: int, order_id: int) -> bool:
    async with async_session() as session:
        stock = await session.get(DigitalStock, id)

        if not stock:
            return False

        stock.order_id = order_id
        await session.commit()
        return True
