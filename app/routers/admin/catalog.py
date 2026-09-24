import enum
from dataclasses import dataclass
from enum import auto

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import settings
from app.keyboards.inline import (
    admin_back_category,
    admin_catalog_keyboard,
    admin_category_serial,
    confirm_create_category,
    render_name_error_keyboard,
)
from app.states import CreateCategoryStates

catalog = Router()


class CategoryNameError(enum.Enum):
    LONG_STRING = auto()
    SHORT_STRING = auto()


@dataclass
class ValidatorResult:
    ok: bool
    error: CategoryNameError | None = None


def _name_validator(name: str) -> ValidatorResult:
    if settings.MINIMUM_LENGTH_CATEGORY > len(name):
        return ValidatorResult(ok=False, error=CategoryNameError.SHORT_STRING)

    elif settings.MAXIMUM_LENGTH_CATEGORY < len(name):
        return ValidatorResult(ok=False, error=CategoryNameError.LONG_STRING)

    return ValidatorResult(ok=True)


async def _render_name_error(message: Message, prompt_message_id: int, error: CategoryNameError):
    match error:
        case CategoryNameError.LONG_STRING:
            text = f"⚠️ Название слишком длинное\nмаксимальная длина: {settings.MAXIMUM_LENGTH_CATEGORY}"
        case CategoryNameError.SHORT_STRING:
            text = f"⚠️ Название слишком короткое\nминимальная длина: {settings.MINIMUM_LENGTH_CATEGORY}"

    if isinstance(message.bot, Bot):
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=prompt_message_id,
            caption=text,
            reply_markup=render_name_error_keyboard,
        )
        await message.delete()


async def _process_category_serial(message: Message, state: FSMContext):
    pass


@catalog.callback_query(F.data == "admin_catalog")
async def catalog_menu(callback: CallbackQuery):
    if callback.message and isinstance(callback.message, Message):
        keyboard = await admin_catalog_keyboard()

        if not keyboard:
            return

        await callback.message.edit_caption(
            caption="Категории и товары",
            reply_markup=keyboard,
        )


@catalog.callback_query(F.data == "create_category")
async def create_category(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, Message):
        await state.set_state(CreateCategoryStates.category_name)
        await state.update_data(prompt_message_id=callback.message.message_id)

        await callback.message.edit_caption(
            caption="Введите название категории",
            reply_markup=admin_back_category,
        )


@catalog.message(CreateCategoryStates.category_name)
async def process_create_category(message: Message, state: FSMContext):
    category_name = message.text
    data = await state.get_data()
    prompt_message_id = data.get("prompt_message_id")

    if isinstance(category_name, str) and prompt_message_id is not None:
        result = _name_validator(name=category_name)

        if result.ok:
            await state.update_data(category_name=category_name)

            if isinstance(message.bot, Bot):
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=prompt_message_id,
                    caption="Введите номер отображения",
                    reply_markup=admin_category_serial,
                )
                await message.delete()

            await state.set_state(CreateCategoryStates.serial_number)

        else:
            assert result.error
            await _render_name_error(message=message, prompt_message_id=prompt_message_id, error=result.error)


@catalog.message(CreateCategoryStates.serial_number)
async def pr_state(message: Message, state: FSMContext):
    position_id = message.text
    await state.update_data(position_id=position_id)
    data = await state.get_data()
    prompt_message_id = data.get("prompt_message_id")

    if isinstance(message.bot, Bot):
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=prompt_message_id,
            caption=f"Потвердите создание\nНазвание категории: {data['category_name']}\nНомер отображения: {position_id}",
            reply_markup=confirm_create_category,
        )
        await message.delete()


@catalog.callback_query(F.data == "admin_category_po_default")
async def pr_callback(callback: CallbackQuery, state: FSMContext):
    position_id = "set_default"
    await state.update_data(position_id=position_id)
    data = await state.get_data()
    prompt_message_id = data.get("prompt_message_id")

    if isinstance(callback.bot, Bot) and isinstance(callback.message, Message):
        await callback.bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=prompt_message_id,
            caption=f"Потвердите создание\nНазвание категории: {data['category_name']}\nНомер отображения: {position_id}",
            reply_markup=confirm_create_category,
        )
