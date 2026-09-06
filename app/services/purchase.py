import enum
from dataclasses import dataclass
from enum import auto

from app.database.queries.balance import deduct_balance, get_balance, top_up_balance
from app.database.queries.digital_stock import get_auto_quantity_stock, get_digital_stock_content, set_order_id
from app.database.queries.manual_stock import get_manual_quantity_stock
from app.database.queries.order import create_order
from app.database.queries.product import get_delivery_type, get_product, set_out_of_stock
from app.enums import DeliveryType
from app.types.products import ProductType


class PurchaseError(enum.Enum):
    PRODUCT_NOT_FOUND = auto()
    NOT_ENOUGH_MONEY = auto()
    OUT_OF_STOCK = auto()
    BALANCE_RACE = auto()


@dataclass
class PurchaseResult:
    ok: bool
    error: PurchaseError | None = None
    order_id: int | None = None
    delivery_type: DeliveryType | None = None
    digital_content: str | None = None
    shortfall: int | None = None


async def _check_auto_stock(product_id: int) -> bool:
    if await get_auto_quantity_stock(product_id) < 1:
        await set_out_of_stock(product_id)
        return False
    return True


async def _check_manual_stock(product_id: int) -> bool:
    if await get_manual_quantity_stock(product_id) < 1:
        await set_out_of_stock(product_id)
        return False
    return True


async def _auto_buy(user_id: int, product_id: int, product_price: int) -> PurchaseResult:
    if not await _check_auto_stock(product_id):
        return PurchaseResult(ok=False, error=PurchaseError.OUT_OF_STOCK)

    if not await deduct_balance(user_id, product_price):
        return PurchaseResult(ok=False, error=PurchaseError.BALANCE_RACE)

    order = await create_order(user_id, product_id, DeliveryType.AUTO, product_price)
    order_id = order["order_id"]

    stock = await get_digital_stock_content(product_id)

    if stock is None:
        await top_up_balance(user_id, product_price)
        await set_out_of_stock(product_id)
        return PurchaseResult(ok=False, error=PurchaseError.OUT_OF_STOCK)

    await set_order_id(stock["id"], order_id)

    return PurchaseResult(ok=True, order_id=order_id, delivery_type=DeliveryType.AUTO, digital_content=stock["content"])


async def _manual_buy(user_id: int, product_id: int, product_price: int) -> PurchaseResult:
    if not await _check_manual_stock(product_id):
        return PurchaseResult(ok=False, error=PurchaseError.OUT_OF_STOCK)

    if not await deduct_balance(user_id, product_price):
        return PurchaseResult(ok=False, error=PurchaseError.BALANCE_RACE)

    order = await create_order(user_id, product_id, DeliveryType.MANUAL, product_price)
    order_id = order["order_id"]

    # заглушка
    return PurchaseResult(ok=True, order_id=order_id, delivery_type=DeliveryType.MANUAL, digital_content="заглушка")


async def buy_product(user_id: int, product_id: int) -> PurchaseResult:
    product = await get_product(product_id)

    if product is None:
        return PurchaseResult(ok=False, error=PurchaseError.PRODUCT_NOT_FOUND)

    product_price = int(product["price"])
    user_balance = await get_balance(user_id)

    if user_balance < product_price:
        return PurchaseResult(ok=False, error=PurchaseError.NOT_ENOUGH_MONEY, shortfall=product_price - user_balance)

    delivery_type = await get_delivery_type(product_id)

    if delivery_type == DeliveryType.AUTO:
        return await _auto_buy(
            user_id=user_id,
            product_id=product_id,
            product_price=product_price,
        )

    elif delivery_type == DeliveryType.MANUAL:
        return await _manual_buy(
            user_id=user_id,
            product_id=product_id,
            product_price=product_price,
        )
