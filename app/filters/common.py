from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from app.database.queries.olds.filters_queries import is_user_subscribed


class IsSubscribed(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return await is_user_subscribed(event.from_user.id) is True


class IsNotSubscribed(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return await is_user_subscribed(event.from_user.id) is False
