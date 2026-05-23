from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


# Categories


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None


class CategoryRead(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Modifiers


class ModifierBase(BaseModel):
    name: str
    price_change: float = 0.0


class ModifierCreate(ModifierBase):
    pass


class ModifierUpdate(BaseModel):
    name: Optional[str] = None
    price_change: Optional[float] = None


class ModifierRead(ModifierBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Menu Items


class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tags: List[str] = Field(default_factory=list)
    active: bool = True


class MenuItemCreate(MenuItemBase):
    category_id: int
    modifier_ids: List[int] = Field(default_factory=list)


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    active: Optional[bool] = None
    tags: Optional[List[str]] = None
    category_id: Optional[int] = None
    modifier_ids: Optional[List[int]] = None


class MenuItemRead(MenuItemBase):
    id: int
    category_id: int
    category: Optional[CategoryRead] = None
    modifiers: List[ModifierRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Order Items


class OrderItemBase(BaseModel):
    item_id: int
    quantity: int = 1
    modifiers: Optional[str] = None


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemStandaloneCreate(OrderItemBase):
    order_id: int


class OrderItemUpdate(BaseModel):
    item_id: Optional[int] = None
    quantity: Optional[int] = None
    modifiers: Optional[str] = None


class OrderItemRead(OrderItemBase):
    id: int
    item: Optional[MenuItemRead] = None

    model_config = ConfigDict(from_attributes=True)


# Orders


class OrderBase(BaseModel):
    status: str = "pending"


class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(default_factory=list)


class OrderUpdate(BaseModel):
    status: Optional[str] = None


class OrderRead(OrderBase):
    id: int
    timestamp: datetime
    items: List[OrderItemRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
