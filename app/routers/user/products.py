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
from app.services.purchase import PurchaseError, PurchaseResult, buy_product
from app.utils.product_builder import product_builder

logger = logging.getLogger(__name__)
product = Router()


async def _render_purchase_error(
    callback: CallbackQuery,
    message: Message,
    result: PurchaseResult,
) -> None:
    match result.error:
        case PurchaseError.PRODUCT_NOT_FOUND:
            await callback.answer("Товар недоступен", show_alert=True)
        case PurchaseError.NOT_ENOUGH_MONEY:
            await message.edit_caption(caption=f"Нехватает {result.shortfall} руб", reply_markup=kb.not_money)
        case PurchaseError.BALANCE_RACE:
            await message.edit_caption(caption="Недостаточно средств", reply_markup=kb.not_money)
        case PurchaseError.OUT_OF_STOCK:
            await message.edit_caption(caption="К сожалению товара нету в наличии", reply_markup=kb.back_main_menu)


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
        return

    product_id = int(callback.data.split("_")[1])

    result = await buy_product(user_id=callback.from_user.id, product_id=product_id)

    if not result.ok and isinstance(callback.message, Message):
        await _render_purchase_error(callback, callback.message, result)
        return

    if result.delivery_type == DeliveryType.AUTO:
        try:
            if isinstance(callback.message, Message) and result.digital_content:
                await callback.message.answer(result.digital_content)
        except Exception:
            logger.exception(
                "Не удалось отправить содержимое товара после списания средств: order_id=%s",
                result.order_id,
            )
            raise
    else:
        if isinstance(callback.message, Message):
            # MANUAL: уведомить, что заявка принята
            await callback.message.edit_caption(
                caption="Заявка принята, ожидайте выдачи", reply_markup=kb.back_main_menu
            )
