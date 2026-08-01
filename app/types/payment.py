from typing import TypedDict


class Payment(TypedDict):
    id: int
    user_id: int
    amount: float
    method: str | None
    status: str
    external_id: str | None
    created_at: str
