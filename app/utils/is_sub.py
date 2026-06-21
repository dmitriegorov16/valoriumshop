import os

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest

CHANNEL_ID = os.getenv("CHANNEL_ID")


async def is_subscribed(bot: Bot, user_id):
    try:
        member = await bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id,
        )
    except TelegramBadRequest:
        return False

    return member.status in {
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    }
