from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto, Message

from app.database.queries.filters import mark_user_subscribed, mark_user_unsubscribed
from app.keyboards import inline as kb
from app.utils.is_sub import is_subscribed


async def sync_subscription_status(bot: Bot, user_id: int) -> bool:
    subscribed = await is_subscribed(bot, user_id)
    if subscribed:
        await mark_user_subscribed(user_id)
    else:
        await mark_user_unsubscribed(user_id)
    return subscribed


async def _show_main_menu(message: Message, user_id: int):
    menu_photo = FSInputFile("images/system/menu_photo.png")
    keyboard = await kb.main_menu_keyboard(user_id)
    await message.answer_photo(
        photo=menu_photo,
        caption="главное меню типа",
        reply_markup=keyboard,
    )


async def _edit_main_menu(message: Message, user_id: int):
    menu_photo = FSInputFile("images/system/menu_photo.png")
    keyboard = await kb.main_menu_keyboard(user_id)
    await message.edit_media(
        media=InputMediaPhoto(
            media=menu_photo,
            caption="главное меню типа",
        ),
        reply_markup=keyboard,
    )
