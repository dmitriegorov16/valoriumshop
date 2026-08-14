from typing import TypedDict


class ProductType(TypedDict):
    id: int
    category_id: int
    name: str
    description: str
    price: int
