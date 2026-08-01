from aiogram.types import FSInputFile, InputMediaPhoto, Message

from app.keyboards import inline as kb


async def show_main_menu(message: Message):
    menu_photo = FSInputFile("images/system/menu_photo.png")
    await message.answer_photo(
        photo=menu_photo,
        caption="главное меню типа",
        reply_markup=kb.main_menu_keyboard,
    )


async def edit_main_menu(message: Message):
    menu_photo = FSInputFile("images/system/menu_photo.png")
    await message.edit_media(
        media=InputMediaPhoto(
            media=menu_photo,
            caption="главное меню типа",
        ),
        reply_markup=kb.main_menu_keyboard,
    )
