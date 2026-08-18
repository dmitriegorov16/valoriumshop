from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from app.database.queries.filters import is_user_subscribed


class IsSubscribed(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        from_user = event.from_user
        if not from_user:
            raise

        return await is_user_subscribed(from_user.id) is True


class IsNotSubscribed(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        from_user = event.from_user
        if not from_user:
            raise

        return await is_user_subscribed(from_user.id) is False
