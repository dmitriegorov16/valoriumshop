from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Bot
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.database.queries.filters import is_user_subscribed
from app.database.queries.user import get_account_type
from app.enums import AccountType
from app.keyboards.inline import check_subscription_keyboard
from app.routers.user import sync_subscription_status


def _is_subscription_check_trigger(event: TelegramObject) -> bool:
    return (
        isinstance(event, Message)
        and event.text == "/start"
        or isinstance(event, CallbackQuery)
        and event.data == "check_subscription"
    )


class AccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ):
        if isinstance(event, (Message, CallbackQuery)):
            db_user = data.get("db_user")

            if db_user:
                account_type = None
                if event.from_user:
                    account_type = await get_account_type(user_id=event.from_user.id)

                if account_type == AccountType.ADMIN:
                    return await handler(event, data)

                # Если это /start или check_subscription - даем доступ сразу
                is_subscription_check_trigger = _is_subscription_check_trigger(event)

                if is_subscription_check_trigger:
                    return await handler(event, data)

                if event.from_user:
                    is_sub = await is_user_subscribed(event.from_user.id)

                    if is_sub:
                        return await handler(event, data)
                    else:
                        if isinstance(event, Message):
                            await event.answer(text="Подпишитесь", reply_markup=check_subscription_keyboard)

                        # TODO: обработка None и InaccessibleMessage
                        elif isinstance(event, CallbackQuery) and isinstance(event.message, Message):
                            await event.answer()
                            await event.message.answer(text="Подпишитесь", reply_markup=check_subscription_keyboard)

                else:
                    # логирование отсутвия event.from_user
                    pass

            elif not db_user:
                is_subscription_check_trigger = _is_subscription_check_trigger(event)

                if is_subscription_check_trigger:
                    data["is_new"] = True
                    return await handler(event, data)
