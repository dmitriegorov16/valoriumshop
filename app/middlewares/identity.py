from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.database.queries.user import user_exists


class IdentityMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ):
        if isinstance(event, (Message, CallbackQuery)) and event.from_user is not None:
            user_id = event.from_user.id
            is_user = await user_exists(user_id)

            if is_user:
                data["db_user"] = True
            else:
                data["db_user"] = False

        return await handler(event, data)
