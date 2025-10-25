import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from db import Base


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    menu_items = relationship(
        "MenuItem", back_populates="category", cascade="all, delete-orphan"
    )


class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    tags = Column(String, nullable=True)
    active = Column(Boolean, nullable=False, default=True)

    modifiers = relationship(
        "Modifier", back_populates="item", cascade="all, delete-orphan"
    )
    category = relationship("Category", back_populates="menu_items")


class Modifier(Base):
    __tablename__ = "modifiers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    price_change = Column(Float, nullable=False, default=0.0)

    item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    item = relationship("MenuItem", back_populates="modifiers")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pending")
    timestamp = Column(DateTime, default=datetime.UTC)

    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    modifiers = Column(String, nullable=True)
    quantity = Column(Integer, default=1)

    order = relationship("Order", back_populates="items")
