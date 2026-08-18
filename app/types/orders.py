from typing import TypedDict

from app.enums import DeliveryType, OrderStatus


class OrderType(TypedDict):
    order_id: int
    user_id: int
    product_id: int
    delivery_type: DeliveryType
    price: int
    status: OrderStatus
