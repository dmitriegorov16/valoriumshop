import enum
from dataclasses import dataclass
from enum import auto

from app.database.queries.category import create_new_category, get_category_serial_number


class CreateCategoryResultError(enum.Enum):
    SERIAL_NUMBER_EXISTS = auto()
    CATEGORY_CREATE_ERROR = auto()


@dataclass
class CreateCategoryResult:
    ok: bool
    error: CreateCategoryResultError | None = None


async def _is_category_serial_exists(serial_number: int) -> bool:
    is_serial = await get_category_serial_number(serial_number)

    return bool(is_serial)


async def create_category(name: str, serial_number: int, set_default: bool) -> CreateCategoryResult:
    # Принимаем имя категории, номер отображения. Потом мы смотрим по номеру отображения,
    # если есть категория с таким номером,
    # то мы сдвигаем все категории с этим номером и выше на 1 вверх.
    # Потом создаем категорию с этим именем и номером отображения.

    if set_default:
        # Если установлено значение по умолчанию, то мы получаем максимальный номер отображения
        pass

    else:
        # Если не установлено значение по умолчанию, то мы проверяем, есть ли категория с таким номером отображения
        is_serial = await _is_category_serial_exists(serial_number)

        if is_serial:
            return CreateCategoryResult(ok=False, error=CreateCategoryResultError.SERIAL_NUMBER_EXISTS)

        else:
            category = await create_new_category(name=name, serial_number=serial_number)

            if category is not None:
                return CreateCategoryResult(ok=False, error=CreateCategoryResultError.CATEGORY_CREATE_ERROR)

    return CreateCategoryResult(ok=True)
