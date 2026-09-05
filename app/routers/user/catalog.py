from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, InaccessibleMessage, InputMediaPhoto, Message

from app.database.queries.category import (
    get_categories,
    get_category_name,
    get_category_parent_id,
    get_category_photo,
    get_subcategories,
)
from app.database.queries.product import get_products
from app.utils.menu_builder import menu_builder
from app.utils.product_builder import products_builder

catalog = Router()


@catalog.callback_query(F.data == "catalog")
async def open_catalog(callback: CallbackQuery):
    await callback.answer("Loading...")
    categories = await get_categories()

    if categories is None:
        # TODO: добавить обработку в logger
        return

    menu_photo = FSInputFile("images/system/catalog_photo.png")

    if isinstance(callback.message, Message):
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=menu_photo,
                caption="Каталог\nВыберите нужный товар",
            ),
            reply_markup=menu_builder(categories, "back_main"),
        )

    elif isinstance(callback.message, InaccessibleMessage):
        # TODO: вывести ошибку про InaccessibleMessage через logger
        return

    else:
        # TODO: вывести ошибку через logger
        return


@catalog.callback_query(F.data.startswith("category_"))
async def open_category(callback: CallbackQuery):
    if callback.data is None:
        # TODO: написать обработку ошибки
        return
    category_id = int(callback.data.split("_")[1])

    category_name = await get_category_name(category_id)
    categories = await get_subcategories(category_id)
    parent_id = await get_category_parent_id(category_id)
    back_callback = f"category_{parent_id}" if parent_id is not None else "back_main"
    category_photo = await get_category_photo(category_id)

    if category_name is None or category_photo is None:
        await callback.answer("Категория недоступна", show_alert=True)
        return

    photo = FSInputFile(f"images/categories/{category_photo}.png")

    if categories:
        reply_markup = menu_builder(categories, back_callback)
    else:
        products = await get_products(category_id)
        reply_markup = products_builder(products, back_callback)

    if isinstance(callback.message, Message):
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=photo,
                caption=f"Категория: {category_name}",
            ),
            reply_markup=reply_markup,
        )

    elif isinstance(callback.message, InaccessibleMessage):
        # TODO: вывести ошибку про InaccessibleMessage через logger
        return

    else:
        # TODO: вывести ошибку через logger
        return
