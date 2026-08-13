from datetime import UTC, datetime

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.enums import *


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "user_info"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    is_sub: Mapped[bool] = mapped_column(default=False)
    balance: Mapped[int] = mapped_column(default=0)
    account_type: Mapped[AccountType] = mapped_column(Enum(AccountType), default=AccountType.USER)
    registered_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))


class Categories(Base):
    __tablename__ = "categories"

    category_id: Mapped[int] = mapped_column(primary_key=True)
    category_name: Mapped[str] = mapped_column(Text)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.category_id"), default=None)
    image: Mapped[str | None] = mapped_column(Text, default=None)


class Products(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.category_id"))
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    price: Mapped[int] = mapped_column()
    image: Mapped[str] = mapped_column()
    delivery_type: Mapped[DeliveryType] = mapped_column(Enum(DeliveryType))
    in_stock: Mapped[bool] = mapped_column(default=False)


class Orders(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_info.user_id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"))
    delivery_type: Mapped[DeliveryType] = mapped_column(Enum(DeliveryType))
    price: Mapped[int] = mapped_column()
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus))


class DigitalStock(Base):
    __tablename__ = "digital_stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id"))
    content: Mapped[str] = mapped_column()
    is_solid = Mapped[bool] = mapped_column(default=False)


class ManualStock(Base):
    __tablename__ = "manual_stock"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"))
    stock_quantity: Mapped[int] = mapped_column(default=0)


class Payments(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_info.user_id"))
    amount: Mapped[float] = mapped_column()
    method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod))
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.DRAFT)
    external_id: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
