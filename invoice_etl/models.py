from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class Item(BaseModel):
    product_id: Optional[str] = None
    product_name: str

    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)


class Invoice(BaseModel):
    order_id: str
    date: date
    customer_id: str

    items: List[Item]

    @property
    def total_value(self) -> float:
        return sum(i.quantity * i.unit_price for i in self.items)
