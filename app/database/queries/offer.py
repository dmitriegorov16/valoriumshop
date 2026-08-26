from sqlalchemy import select

from app.database.engine import async_session
from app.database.models import UserAgreement


async def create_agreement(user_id: int):
    async with async_session() as session:
        agreement = UserAgreement(
            user_id=user_id,
        )
        session.add(agreement)
        await session.commit()
