import logging
import os

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest

from app.config import settings

logger = logging.getLogger(__name__)


async def is_subscribed(bot: Bot, user_id):
    try:
        member = await bot.get_chat_member(
            chat_id=settings.CHANNEL_ID,
            user_id=user_id,
        )
    except TelegramBadRequest:
        logger.exception(
            "Ошибка Telegram API при проверке подписки: user_id=%s, channel_id=%s",
            user_id,
            settings.CHANNEL_ID,
        )
        return False

    return member.status in {
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    }
