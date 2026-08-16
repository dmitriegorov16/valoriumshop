from typing import TypedDict


class CategoryType(TypedDict):
    id: int
    name: str
    parent_id: int | None
    photo: str | None
