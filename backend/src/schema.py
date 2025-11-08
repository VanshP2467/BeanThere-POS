from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

# Categories


class CategorySchema(BaseModel):
    name: str


class CategoryCreate(CategorySchema):
    pass


class CategoryRead(CategorySchema):
    id: int

    class Config:
        from_attributes = True


## Modifiers


class ModifierSchema(BaseModel):
    name: str
    price_change: float = 0.0


class ModifierCreate(ModifierSchema):
    pass


class ModifierRead(ModifierSchema):
    id: int

    class Config:
        from_attributes = True


# MenuItems


class MenuItemSchema(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    active: bool = True
    tags: Optional[List[str]] = []


class MenuItemCreate(MenuItemSchema):
    category_id: int
    modifier_ids: Optional[List[int]] = []


class MenuItemRead(MenuItemSchema):
    id: int
    category: Optional[CategoryRead]
    modifiers: Optional[List[ModifierRead]] = []

    class Config:
        from_attributes = True


class OrderItemSchema(BaseModel):
    item_id: int
    quantity: int = 1
    modifiers: Optional[str] = None


class OrderItemCreate(OrderItemSchema):
    pass


class OrderItemRead(OrderItemSchema):
    id: int
    item: Optional[MenuItemRead]

    class Config:
        from_attributes = True


class OrderSchema(BaseModel):
    status: str = "pending"


class OrderCreate(OrderSchema):
    items: List[OrderItemCreate]


class OrderRead(OrderSchema):
    id: int
    timestamp: datetime
    items: List[OrderItemRead] = []

    class Config:
        from_attributes = True
