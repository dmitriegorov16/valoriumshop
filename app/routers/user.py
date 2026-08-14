import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message, PreCheckoutQuery
from aiosend.types import Invoice

from app.database.queries.olds.balance_queries import deduct_balance, get_balance, top_up_balance
from app.database.queries.olds.categories_queries import (
    get_categories,
    get_category_name,
    get_category_parent_id,
    get_category_photo,
    get_subcategories,
)
from app.database.queries.olds.filters_queries import mark_user_subscribed, mark_user_unsubscribed
from app.database.queries.olds.orders_queries import create_order
from app.database.queries.olds.payments_queries import (
    create_payment,
    get_amount,
    get_payment,
    mark_payment_paid,
    update_payment_method,
)
from app.database.queries.olds.products_queries import (
    get_delivery_type,
    get_product,
    get_product_photo,
    get_products,
    set_out_of_stock,
)
from app.database.queries.olds.stock_queries import (
    get_auto_quantity_stock,
    get_digital_stock_content,
    get_manual_quantity_stock,
    set_order_id,
)
from app.database.queries.olds.user_queries import get_registered_at, new_registration
from app.filters.common import IsSubscribed
from app.keyboards import inline as kb
from app.payments.crypto_bot import cp, create_crypto_bot_invoice
from app.payments.stars import create_stars_invoice_link
from app.states import PaymentStates
from app.utils.is_sub import is_subscribed
from app.utils.menu import edit_main_menu, show_main_menu
from app.utils.menu_builder import menu_builder
from app.utils.product_builder import product_builder, products_builder

logger = logging.getLogger(__name__)

user = Router()
user.message.filter(IsSubscribed())
user.callback_query.filter(IsSubscribed())


async def sync_subscription_status(bot: Bot, user_id: int) -> bool:
    subscribed = await is_subscribed(bot, user_id)
    if subscribed:
        await mark_user_subscribed(user_id)
    else:
        await mark_user_unsubscribed(user_id)
    return subscribed


@user.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    await new_registration(user_id)

    subscribed = await sync_subscription_status(message.bot, user_id)

    if subscribed:
        await show_main_menu(message, user_id)
    else:
        await message.answer_photo(
            "Перед началом подпишитесь на наш канал:",
            reply_markup=kb.check_subscription_keyboard,
        )


@user.callback_query(F.data == "catalog")
async def catalog(callback: CallbackQuery):
    await callback.answer("Loading...")
    categories = await get_categories()
    menu_photo = FSInputFile("images/system/catalog_photo.png")

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=menu_photo,
            caption="Каталог\nВыберите нужный товар",
        ),
        reply_markup=menu_builder(categories, "back_main"),
    )


@user.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    await callback.answer("Loading...")
    user_id = callback.from_user.id
    profile_photo = FSInputFile("images/system/profile_photo.png")
    balance = await get_balance(user_id)
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=profile_photo,
            caption=f"Профиль\n{balance} руб",
        ),
        reply_markup=kb.profile_keyboard,
    )


@user.callback_query(F.data == "top_up")
async def top_up(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Loading...")
    topup_photo = FSInputFile("images/system/topup.png")

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=topup_photo,
            caption="Введите сумму пополнения в рублях (минимум 50 руб)",
        ),
        reply_markup=kb.back_profile_keyboard,
    )
    await state.update_data(
        bot_message_id=callback.message.message_id,
        bot_chat_id=callback.message.chat.id,
    )
    await state.set_state(PaymentStates.amount)


@user.message(PaymentStates.amount)
async def process_amount(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    if not message.text or not message.text.isdigit():
        try:
            await bot.edit_message_caption(
                chat_id=data["bot_chat_id"],
                message_id=data["bot_message_id"],
                caption="Пожалуйста, введите число",
                reply_markup=kb.back_profile_keyboard,
            )
        except TelegramBadRequest:
            pass
        await message.delete()
        return

    amount = int(message.text)
    if amount < 50:
        try:
            await bot.edit_message_caption(
                chat_id=data["bot_chat_id"],
                message_id=data["bot_message_id"],
                caption="Минимальная сумма — 50 руб",
                reply_markup=kb.back_profile_keyboard,
            )
        except TelegramBadRequest:
            pass
        await message.delete()
        return

    # amount уже int, повторное присваивание message.text убрано — это и был баг
    user_id = message.from_user.id
    payment_id = await create_payment(user_id, amount)
    await state.update_data(payment_id=payment_id)
    await state.set_state(None)

    data = await state.get_data()
    await bot.edit_message_caption(
        chat_id=data["bot_chat_id"],
        message_id=data["bot_message_id"],
        caption=f"Пополнение на {amount} р\nВыберете метод оплаты",
        reply_markup=kb.selection_method,
    )

    await message.delete()


@user.callback_query(F.data == "sbp_selection")
async def process_sbp(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Loading...")

    data = await state.get_data()
    payment_id = data["payment_id"]

    await update_payment_method(payment_id, "sbp")

    await callback.message.edit_caption(
        caption="Сбпь",
        reply_markup=kb.cancel_payment,
    )


@user.callback_query(F.data == "crypto_bot_selection")
async def process_crypto_bot(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Loading...")

    data = await state.get_data()
    payment_id = data["payment_id"]

    await update_payment_method(payment_id, "crypto_bot")
    amount = await get_amount(payment_id)

    payment_link = await create_crypto_bot_invoice(
        amount,
        payment_id,
        callback.message,
    )

    await callback.message.edit_caption(
        caption=f"Оплата {amount} руб",
        reply_markup=kb.create_crypto_bot_payment(payment_link),
    )


@cp.invoice_paid()
async def handle_payment(invoice: Invoice, message: Message):
    payment_id = invoice.payload
    charge_id = invoice.invoice_id
    user_id = message.from_user.id

    if not await mark_payment_paid(payment_id, charge_id):
        # платёж уже был обработан ранее (повторный вебхук) либо payment_id некорректен —
        # баланс НЕ трогаем, чтобы не начислить его дважды
        logger.warning("Повторная или некорректная обработка оплаты payment_id=%s", payment_id)
        return

    amount = await get_amount(payment_id)
    await top_up_balance(user_id, amount)
    logger.info(
        "Зачислена оплата CryptoBot: payment_id=%s, user_id=%s, amount=%s руб, invoice_id=%s",
        payment_id,
        user_id,
        amount,
        charge_id,
    )
    await message.answer("Оплата прошла успешно! ✅")


@user.callback_query(F.data == "stars_selection")
async def process_stars(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer("Loading...")

    data = await state.get_data()
    payment_id = data["payment_id"]

    await update_payment_method(payment_id, "stars")
    amount = await get_amount(payment_id)

    payment_link = await create_stars_invoice_link(
        bot,
        payment_id,
        amount,
    )

    await callback.message.edit_caption(
        caption=f"Оплата {amount} руб",
        reply_markup=kb.create_stars_payment(payment_link),
    )


@user.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    payment_id = pre_checkout_query.invoice_payload
    payment = await get_payment(payment_id)

    if payment is None or payment["status"] == "paid":
        logger.warning(
            "Отклонён pre_checkout: payment_id=%s, user_id=%s, status=%s",
            payment_id,
            pre_checkout_query.from_user.id,
            payment["status"] if payment else "not_found",
        )
        await pre_checkout_query.answer(
            ok=False,
            error_message="Платёж недоступен, попробуйте создать новый.",
        )
        return

    await pre_checkout_query.answer(ok=True)


@user.message(F.successful_payment)
async def process_successful_payment(message: Message, bot: Bot):
    payment_id = message.successful_payment.invoice_payload
    telegram_charge_id = message.successful_payment.telegram_payment_charge_id
    user_id = message.from_user.id

    if not await mark_payment_paid(payment_id, telegram_charge_id):
        logger.warning("Повторная или некорректная обработка оплаты payment_id=%s", payment_id)
        return

    amount = await get_amount(payment_id)
    await top_up_balance(user_id, amount)
    logger.info(
        "Зачислена оплата Stars: payment_id=%s, user_id=%s, amount=%s руб, charge_id=%s",
        payment_id,
        user_id,
        amount,
        telegram_charge_id,
    )
    await message.answer("Оплата прошла успешно! ✅")


@user.callback_query(F.data.startswith("category_"))
async def open_category(callback: CallbackQuery):
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

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=f"Категория: {category_name}",
        ),
        reply_markup=reply_markup,
    )


@user.callback_query(F.data.startswith("product_"))
async def open_product(callback: CallbackQuery):
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
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=f"{product['name']}\n\n{product['description']}\n\nЦена: {product['price']}",
        ),
        reply_markup=product_builder(product_id, back_callback),
    )


@user.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: CallbackQuery):
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
        await callback.message.edit_caption(
            caption=f"Нехватает {abs(user_balance - product_price)} руб",
            reply_markup=kb.not_money,
        )
        return

    delivery_type = await get_delivery_type(product_id)

    if delivery_type == "auto":
        quantity_stock = await get_auto_quantity_stock(product_id)
        if quantity_stock < 1:
            await callback.message.edit_caption(
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
            await callback.message.edit_caption(
                caption="Недостаточно средств",
                reply_markup=kb.not_money,
            )
            return

        order_id = await create_order(user_id, product_id, delivery_type, product_price)
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
            await callback.message.edit_caption(
                caption="К сожалению товара нету в наличии",
                reply_markup=kb.back_main_menu,
            )
            await set_out_of_stock(product_id)
            return

        await set_order_id(stock["id"], order_id)

        try:
            await callback.message.answer(stock["content"])
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

    elif delivery_type == "manual":
        quantity_stock = await get_manual_quantity_stock(product_id)
        if quantity_stock < 1:
            await callback.message.edit_caption(
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
            await callback.message.edit_caption(
                caption="Недостаточно средств",
                reply_markup=kb.not_money,
            )
            return

        order_id = await create_order(user_id, product_id, delivery_type, product_price)
        logger.info(
            "Создан заказ на ручную выдачу: user_id=%s, product_id=%s, order_id=%s, amount=%s руб",
            user_id,
            product_id,
            order_id,
            product_price,
        )
        # дописать manual выдачу


@user.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    user_id = callback.from_user.id

    subscribed = await sync_subscription_status(callback.bot, user_id)

    if subscribed:
        await edit_main_menu(callback.message, user_id)
    else:
        await callback.message.answer(
            "Перед началом подпишитесь на наш канал:",
            reply_markup=kb.check_subscription_keyboard,
        )
