from sqlalchemy import select

from app.database.engine import async_session
from app.database.models import User


async def mark_user_subscribed(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.user_id == user_id),
        )
        user = result.scalar_one()
        user.is_sub = True
        await session.commit()


async def mark_user_unsubscribed(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.user_id == user_id),
        )
        user = result.scalar_one()
        user.is_sub = False
        await session.commit()


async def is_user_subscribed(user_id: int) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.user_id == user_id),
        )
        user = result.scalar_one_or_none()

        return user.is_sub if user is not None else False
