from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 2, answer_range: float = 4):
        self.cache: TTLCache[int, bool] = TTLCache(maxsize=10_000, ttl=rate_limit)
        self.throttle_cache: TTLCache[int, bool] = TTLCache(maxsize=10_000, ttl=answer_range)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:

        if isinstance(event, (Message, CallbackQuery)) and event.from_user:
            user_id = event.from_user.id
        else:
            return await handler(event, data)

        if user_id in self.cache:
            if user_id in self.throttle_cache:
                print("скип")
                if isinstance(event, CallbackQuery):
                    await event.answer()
            else:
                self.throttle_cache[user_id] = True

                if isinstance(event, Message):
                    await event.answer("Пожалуйста, подождите")
                    print("юзер ждет message")
                elif isinstance(event, CallbackQuery):
                    await event.answer("Пожалуйста, подождите", show_alert=True)
                    print("alert отправлен успешно")

        else:
            self.cache[user_id] = True
            print("успешно")
            return await handler(event, data)
