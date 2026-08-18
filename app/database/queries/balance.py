from sqlalchemy import delete, select, update

from app.database.engine import async_session
from app.database.models import User


async def get_balance(user_id: int) -> int:
    async with async_session() as session:
        result = await session.execute(
            select(User.balance).where(User.user_id == user_id),
        )
        balance = result.scalar_one()
        return balance


async def top_up_balance(user_id: int, amount: int) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.user_id == user_id),
        )
        user = result.scalar_one_or_none()

        if not user:
            return False

        user.balance += amount
        await session.commit()
        return True


async def deduct_balance(user_id: int, amount: int) -> bool:
    if amount <= 0:
        return False

    async with async_session() as session:
        stmt = update(User).where(User.user_id == user_id, User.balance >= amount).values(balance=User.balance - amount)
        result = await session.execute(stmt)
        await session.commit()

        return result.rowcount > 0  # ty: ignore[unresolved-attribute]
