from datetime import datetime
from typing import TypedDict

from app.enums import PaymentMethod, PaymentStatus


class PaymentType(TypedDict):
    id: int
    user_id: int
    amount: float
    method: PaymentMethod
    status: PaymentStatus
    external_id: str | None
    created_at: datetime
