from sqlalchemy import delete, select, update

from app.database.engine import async_session
from app.database.models import Product
from app.enums import DeliveryType
from app.types.products import ProductType


async def get_products(category_id: int) -> list[ProductType]:
    async with async_session() as session:
        result = await session.execute(
            select(Product).where(Product.category_id == category_id),
        )
        products = result.scalars().all()

        return [
            ProductType(
                id=product.product_id,
                category_id=product.category_id,
                name=product.name,
                description=product.description,
                price=product.price,
            )
            for product in products
        ]


async def get_product(product_id: int) -> ProductType | None:
    async with async_session() as session:
        result = await session.execute(
            select(Product).where(Product.product_id == product_id),
        )

        product = result.scalar_one_or_none()

        if not product:
            return None

        return ProductType(
            id=product.product_id,
            category_id=product.category_id,
            name=product.name,
            description=product.description,
            price=product.price,
        )


async def get_product_photo(product_id: int) -> str | None:
    async with async_session() as session:
        result = await session.execute(select(Product.image).where(Product.product_id == product_id))

        image = result.scalar_one_or_none()
        return image


async def get_delivery_type(product_id: int) -> DeliveryType:
    async with async_session() as session:
        result = await session.execute(select(Product.delivery_type).where(Product.product_id == product_id))

        delivery_type = result.scalar_one_or_none()
        return delivery_type


async def set_out_of_stock(product_id: int) -> bool:
    async with async_session() as session:
        product = await session.get(Product, product_id)

        if not product:
            return False

        product.in_stock = False
        await session.commit()
        return True
