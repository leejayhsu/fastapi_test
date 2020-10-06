from typing import Optional
from pydantic import BaseModel


class ItemSchema(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    # tax: Optional[float] = None

    class Config:
        orm_mode = True

