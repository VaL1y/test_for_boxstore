from pydantic import BaseModel, field_validator
from datetime import date
from typing import Literal

Marketplace = Literal["ozon", "wildberries", "yandex_market"]
Status = Literal["delivered", "returned", "cancelled"]


class Sale(BaseModel):
    order_id: str
    marketplace: Marketplace
    product_name: str
    quantity: int
    price: float
    cost_price: float
    status: Status
    sold_at: date

    @field_validator("price", "cost_price")
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("price и cost_price должны быть > 0")
        return v

    @field_validator("quantity")
    def validate_quantity(cls, v):
        if v < 1:
            raise ValueError("quantity должен быть >= 1")
        return v

    @field_validator("sold_at")
    def validate_date(cls, v):
        if v > date.today():
            raise ValueError("Дата не может быть из будущего")
        return v