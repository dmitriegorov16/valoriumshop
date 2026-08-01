from typing import TypedDict


class Product(TypedDict):
    id: int
    category_id: int
    name: str
    description: str
    price: int
