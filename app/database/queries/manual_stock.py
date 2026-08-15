from sqlalchemy import delete, func, select, update

from app.database.engine import async_session
from app.database.models import ManualStock


async def get_manual_quantity_stock(product_id: int) -> int:
    async with async_session() as session:
        result = await session.execute(
            select(ManualStock.stock_quantity).where(ManualStock.product_id == product_id)
        )
        quantity_stock = result.scalar_one()
        return quantity_stock
