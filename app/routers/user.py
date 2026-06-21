from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.filters.common import IsSubscribed
from app.utils.menu import show_main_menu

user = Router()
user.message.filter(IsSubscribed())
user.callback_query.filter(IsSubscribed())


@user.message(CommandStart())
async def cmd_start(message: Message):
    await show_main_menu(message)
