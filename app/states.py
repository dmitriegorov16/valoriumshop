from aiogram.fsm.state import State, StatesGroup


class PaymentStates(StatesGroup):
    amount = State()


class RegistrationStates(StatesGroup):
    user_id = State()


class CreateCategoryStates(StatesGroup):
    category_name = State()
    serial_number = State()
