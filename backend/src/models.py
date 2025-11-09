from __future__ import annotations

from datetime import datetime, timezone

from typing import Optional, List
from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    Float,
    Boolean,
    JSON,
    Text,
    Table,
    Column,
    DateTime,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped
from backend.src.db import Base


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    menu_items: Mapped[List["MenuItem"]] = relationship(
        "MenuItem", back_populates="category", cascade="all, delete-orphan"
    )


menu_item_modifiers = Table(
    "menu_item_modifiers",
    Base.metadata,
    Column("menu_item_id", ForeignKey("menu_items.id"), primary_key=True),
    Column("modifier_id", ForeignKey("modifiers.id"), primary_key=True),
)


class MenuItem(Base):
    __tablename__ = "menu_items"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(50), index=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))
    description: Mapped[Optional[str]] = mapped_column(Text)

    modifiers: Mapped[Optional[List["Modifier"]]] = relationship(
        back_populates="menu_items", secondary=menu_item_modifiers
    )
    category: Mapped["Category"] = relationship("Category", back_populates="menu_items")

    price: Mapped[float] = mapped_column(Float, default=0.0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=[])


class Modifier(Base):
    __tablename__ = "modifiers"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    menu_items: Mapped[List["MenuItem"]] = relationship(
        "MenuItem",
        back_populates="modifiers",
        secondary=menu_item_modifiers,
    )
    price_change: Mapped[float] = mapped_column(Float, default=0.0)


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    status: Mapped[str] = mapped_column(String(50), default="pending")
    timestamp: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"))
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("menu_items.id"))
    modifiers: Mapped[Optional[str]] = mapped_column(String(50))

    order: Mapped["Order"] = relationship(
        back_populates="items",
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1)
