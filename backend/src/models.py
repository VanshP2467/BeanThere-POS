import datetime
from typing import Optional, List

from sqlalchemy import Integer, String, ForeignKey, Float, Boolean, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from db import Base


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)

    menu_items: Mapped[List["MenuItem"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )


class MenuItem(Base):
    __tablename__ = "menu_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))
    description: Mapped[Optional[str]] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    tags: Mapped[Optional[str]] = mapped_column(String)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    modifiers: Mapped[List["Modifier"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )
    category: Mapped["Category"] = relationship(back_populates="menu_items")


class Modifier(Base):
    __tablename__ = "modifiers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    price_change: Mapped[float] = mapped_column(Float, default=0.0)

    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("menu_items.id"))
    item: Mapped["MenuItem"] = relationship(back_populates="modifiers")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    timestamp: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"))
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("menu_items.id"))
    modifiers: Mapped[Optional[str]] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    order: Mapped["Order"] = relationship(back_populates="items")
