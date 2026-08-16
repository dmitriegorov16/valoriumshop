from sqlalchemy import delete, select, update

from app.database.engine import async_session
from app.database.models import Payment
from app.enums import PaymentMethod, PaymentStatus
from app.types.payment import PaymentType


async def create_payment(user_id: int, amount: int) -> int:
    async with async_session() as session:
        payment = Payment(user_id=user_id, amount=amount)
        session.add(payment)
        await session.commit()
        return payment.payment_id


async def get_payment(payment_id: int) -> PaymentType | None:
    async with async_session() as session:
        result = await session.execute(
            select(Payment).where(Payment.payment_id == payment_id),
        )
        payment = result.scalar_one_or_none()

        if not payment:
            return None

        return PaymentType(
            id=payment.payment_id,
            user_id=payment.user_id,
            amount=payment.amount,
            method=payment.method,
            status=payment.status,
            created_at=payment.created_at,
            external_id=payment.external_id,
        )


async def update_payment_method(payment_id: int, method: PaymentMethod) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(Payment).where(Payment.payment_id == payment_id),
        )
        payment = result.scalar_one_or_none()

        if not payment:
            return False

        payment.method = method
        await session.commit()
        return True


# TODO: Добавить валидацию для external_id
async def mark_payment_paid(payment_id: int, external_id: str) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(Payment).where(Payment.payment_id == payment_id),
        )
        payment = result.scalar_one_or_none()
        if not payment:
            return False

        payment.status = PaymentStatus.PAID
        payment.external_id = external_id
        await session.commit()
        return True


async def get_amount(payment_id: int) -> float:
    async with async_session() as session:
        result = await session.execute(
            select(Payment.amount).where(Payment.payment_id == payment_id),
        )
        amount = result.scalar_one()
        return amount
