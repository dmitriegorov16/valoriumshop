import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, InaccessibleMessage, InputMediaPhoto, Message

import app.keyboards.inline as kb
from app.database.queries.balance import deduct_balance, get_balance, top_up_balance
from app.database.queries.digital_stock import get_auto_quantity_stock, get_digital_stock_content, set_order_id
from app.database.queries.manual_stock import get_manual_quantity_stock
from app.database.queries.order import create_order
from app.database.queries.product import get_delivery_type, get_product, get_product_photo, set_out_of_stock
from app.enums import DeliveryType
from app.utils.product_builder import product_builder

logger = logging.getLogger(__name__)
product = Router()


@product.callback_query(F.data.startswith("product_"))
async def open_product(callback: CallbackQuery):
    if callback.data is None:
        # TODO: вывести ошибку через logger
        return

    product_id = int(callback.data.split("_")[1])
    product = await get_product(product_id)

    if product is None:
        await callback.answer("Товар недоступен", show_alert=True)
        return

    back_callback = f"category_{product['category_id']}"
    product_photo = await get_product_photo(product_id)

    if product_photo is None:
        await callback.answer("Товар недоступен", show_alert=True)
        return

    photo = FSInputFile(f"images/products/{product_photo}.png")
    if isinstance(callback.message, Message):
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=photo,
                caption=f"{product['name']}\n\n{product['description']}\n\nЦена: {product['price']}",
            ),
            reply_markup=product_builder(product_id, back_callback),
        )

    elif isinstance(callback.message, InaccessibleMessage):
        # TODO: вывести ошибку про InaccessibleMessage через logger
        return

    else:
        # TODO: вывести ошибку через logger
        return


@product.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: CallbackQuery):
    if callback.data is None:
        # TODO: вывести ошибку через logger
        return

    if isinstance(callback.message, InaccessibleMessage):
        # TODO: вывести ошибку про InaccessibleMessage через logger
        return

    if not isinstance(callback.message, Message):
        # TODO: вывести ошибку через logger
        return

    message = callback.message

    product_id = int(callback.data.split("_")[1])
    product = await get_product(product_id)

    if product is None:
        await callback.answer("Товар недоступен", show_alert=True)
        return

    product_price = int(product["price"])
    user_id = callback.from_user.id
    user_balance = int(await get_balance(user_id))

    if user_balance < product_price:
        logger.warning(
            "Недостаточно средств: user_id=%s, product_id=%s, balance=%s, price=%s",
            user_id,
            product_id,
            user_balance,
            product_price,
        )
        await message.edit_caption(
            caption=f"Нехватает {abs(user_balance - product_price)} руб",
            reply_markup=kb.not_money,
        )
        return

    delivery_type = await get_delivery_type(product_id)

    if delivery_type == DeliveryType.AUTO:
        quantity_stock = await get_auto_quantity_stock(product_id)
        if quantity_stock < 1:
            await message.edit_caption(
                caption="К сожалению товара нету в наличии",
                reply_markup=kb.back_main_menu,
            )
            await set_out_of_stock(product_id)
            return

        # сначала атомарно списываем баланс, и только потом выдаём товар —
        # иначе при гонке товар может уйти бесплатно
        if not await deduct_balance(user_id, product_price):
            logger.warning(
                "Гонка при списании баланса: проверка прошла, списание не удалось — "
                "user_id=%s, product_id=%s, price=%s",
                user_id,
                product_id,
                product_price,
            )
            await message.edit_caption(
                caption="Недостаточно средств",
                reply_markup=kb.not_money,
            )
            return

        order = await create_order(user_id, product_id, delivery_type, product_price)
        order_id = order["order_id"]

        stock = await get_digital_stock_content(product_id)

        if stock is None:
            logger.error(
                "Товар не выдан после списания средств, выполняется возврат: "
                "user_id=%s, product_id=%s, order_id=%s, amount=%s руб",
                user_id,
                product_id,
                order_id,
                product_price,
            )
            # баланс уже списан, а товар кончился между проверкой и выдачей —
            # возвращаем деньги, чтобы не оставить пользователя без товара и без денег
            await top_up_balance(user_id, product_price)
            await message.edit_caption(
                caption="К сожалению товара нету в наличии",
                reply_markup=kb.back_main_menu,
            )
            await set_out_of_stock(product_id)
            return

        await set_order_id(stock["id"], order_id)

        try:
            await message.answer(stock["content"])
        except Exception:
            # деньги уже списаны, а содержимое товара не доставлено пользователю
            logger.exception(
                "Не удалось отправить содержимое товара после списания средств: "
                "user_id=%s, product_id=%s, order_id=%s, stock_id=%s, amount=%s руб",
                user_id,
                product_id,
                order_id,
                stock["id"],
                product_price,
            )
            raise

        logger.info(
            "Цифровой товар выдан: user_id=%s, product_id=%s, order_id=%s, stock_id=%s, amount=%s руб",
            user_id,
            product_id,
            order_id,
            stock["id"],
            product_price,
        )

    elif delivery_type == DeliveryType.MANUAL:
        quantity_stock = await get_manual_quantity_stock(product_id)
        if quantity_stock < 1:
            await message.edit_caption(
                caption="К сожалению товара нету в наличии",
                reply_markup=kb.back_main_menu,
            )
            await set_out_of_stock(product_id)
            return

        if not await deduct_balance(user_id, product_price):
            logger.warning(
                "Гонка при списании баланса: проверка прошла, списание не удалось — "
                "user_id=%s, product_id=%s, price=%s",
                user_id,
                product_id,
                product_price,
            )
            await message.edit_caption(
                caption="Недостаточно средств",
                reply_markup=kb.not_money,
            )
            return

        order = await create_order(user_id, product_id, delivery_type, product_price)
        order_id = order["order_id"]
        logger.info(
            "Создан заказ на ручную выдачу: user_id=%s, product_id=%s, order_id=%s, amount=%s руб",
            user_id,
            product_id,
            order_id,
            product_price,
        )
        # дописать manual выдачу
