from datetime import datetime

from sqlalchemy import select

from app.database.engine import async_session
from app.database.models import User
from app.enums import AccountType


async def new_registration(user_id: int) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.user_id == user_id),
        )

        is_user = result.scalar_one_or_none()

        if is_user:
            return False
        else:
            user = User(user_id=user_id)
            session.add(user)
            await session.commit()
            return True


async def user_exists(user_id: int) -> bool:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()

        return bool(user)


async def get_registered_at(user_id: int) -> datetime | None:
    async with async_session() as session:
        result = await session.execute(
            select(User.registered_at).where(User.user_id == user_id),
        )

        registered_at = result.scalar_one_or_none()
        return registered_at


async def get_account_type(user_id: int) -> AccountType | None:
    async with async_session() as session:
        result = await session.execute(
            select(User.account_type).where(User.user_id == user_id),
        )

        account_type = result.scalar_one_or_none()
        return account_type
