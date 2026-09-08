from aiogram.types import FSInputFile, InputMediaPhoto, Message

from app.keyboards.inline import admin_menu_keyboard


async def _show_admin_menu(message: Message):
    menu_photo = FSInputFile("images/system/admin.png")
    keyboard = await admin_menu_keyboard()
    await message.answer_photo(
        photo=menu_photo,
        caption="Админ панель",
        reply_markup=keyboard,
    )


async def _edit_admin_menu(message: Message):
    menu_photo = FSInputFile("images/system/admin.png")
    keyboard = await admin_menu_keyboard()
    await message.edit_media(
        media=InputMediaPhoto(
            media=menu_photo,
            caption="Админ панель",
        ),
        reply_markup=keyboard,
    )
