from sqlalchemy import delete, select, update

from app.database.engine import async_session
from app.database.models import Order
from app.enums import DeliveryType
from app.types.orders import OrderType


async def create_order(user_id: int, product_id: int, delivery_type: DeliveryType, price: int) -> OrderType:
    async with async_session() as session:
        order = Order(
            user_id=user_id,
            product_id=product_id,
            delivery_type=delivery_type,
            price=price,
        )
        session.add(order)
        await session.commit()
        return OrderType(
            order_id=order.order_id,
            user_id=order.user_id,
            product_id=order.product_id,
            delivery_type=order.delivery_type,
            price=order.price,
            status=order.status,
        )
