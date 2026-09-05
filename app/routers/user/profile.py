from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, InaccessibleMessage, InputMediaPhoto, Message

import app.keyboards.inline as kb
from app.database.queries.balance import get_balance

profile = Router()


@profile.callback_query(F.data == "profile")
async def open_profile(callback: CallbackQuery):
    await callback.answer("Loading...")
    user_id = callback.from_user.id
    profile_photo = FSInputFile("images/system/profile_photo.png")
    balance = await get_balance(user_id)

    if isinstance(callback.message, Message):
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=profile_photo,
                caption=f"Профиль\n{balance} руб",
            ),
            reply_markup=kb.profile_keyboard,
        )

    elif isinstance(callback.message, InaccessibleMessage):
        # TODO: вывести ошибку про InaccessibleMessage через logger
        return

    else:
        # TODO: вывести ошибку через logger
        return
