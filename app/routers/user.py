from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message, PreCheckoutQuery
from aiosend.types import Invoice

from app.database.queries.balance_queries import get_balance, top_up_balance
from app.database.queries.categories_queries import (
    get_categories,
    get_category_name,
    get_category_parent_id,
    get_category_photo,
    get_subcategories,
)
from app.database.queries.filters_queries import mark_user_subscribed, mark_user_unsubscribed
from app.database.queries.payments_queries import (
    create_payment,
    get_amount,
    get_payment,
    mark_payment_paid,
    update_payment_method,
)
from app.database.queries.products_queries import get_product, get_product_photo, get_products
from app.database.queries.user_queries import get_registered_at
from app.filters.common import IsSubscribed
from app.keyboards import inline as kb
from app.payments.crypto_bot import cp, create_crypto_bot_invoice
from app.payments.stars import create_stars_invoice_link
from app.states import PaymentStates
from app.utils.is_sub import is_subscribed
from app.utils.menu import edit_main_menu, show_main_menu
from app.utils.menu_builder import menu_builder
from app.utils.product_builder import product_builder

user = Router()
user.message.filter(IsSubscribed())
user.callback_query.filter(IsSubscribed())


@user.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id

    subscribed = await is_subscribed(message.bot, user_id)

    if subscribed:
        await show_main_menu(message)
    else:
        await mark_user_unsubscribed(user_id)
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

    amount = message.text
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

    await mark_payment_paid(payment_id, charge_id)

    await message.answer("Оплата прошла успешно! ✅")
    amount = await get_amount(payment_id)
    await top_up_balance(user_id, amount)


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
    await mark_payment_paid(payment_id, telegram_charge_id)

    await message.answer("Оплата прошла успешно! ✅")
    amount = await get_amount(payment_id)
    await top_up_balance(user_id, amount)


@user.callback_query(F.data.startswith("category_"))
async def open_category(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    category_name = await get_category_name(category_id)
    categories = await get_subcategories(category_id)
    parent_id = await get_category_parent_id(category_id)
    back_callback = f"category_{parent_id}" if parent_id is not None else "back_main"
    category_photo = await get_category_photo(category_id)
    photo = FSInputFile(f"images/categories/{category_photo}.png")

    if categories:
        reply_markup = menu_builder(categories, back_callback)
    else:
        products = await get_products(category_id)
        reply_markup = product_builder(products, back_callback)

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
    back_callback = f"category_{product['category_id']}"
    product_photo = await get_product_photo(product_id)
    photo = FSInputFile(f"images/products/{product_photo}.png")
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=f"{product['name']}\n\n{product['description']}\n\nЦена: {product['price']}",
        ),
        reply_markup=product_builder([], back_callback),
    )


@user.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    user_id = callback.from_user.id

    subscribed = await is_subscribed(callback.bot, user_id)

    if subscribed:
        await edit_main_menu(callback.message)
    else:
        await mark_user_unsubscribed(user_id)
        await callback.message.answer(
            "Перед началом подпишитесь на наш канал:",
            reply_markup=kb.check_subscription_keyboard,
        )
