from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.src.db import get_db
from backend.src.schema import (
    OrderItemRead,
    OrderItemStandaloneCreate,
    OrderItemUpdate,
)
from backend.src.crud import order_items as crud_order_items

router = APIRouter(
    prefix="/order_items",
    tags=["Order Items"],
)


@router.get("/", response_model=list[OrderItemRead])
def list_order_items(
    order_id: int | None = None, db: Session = Depends(get_db)
):
    return crud_order_items.get_order_items(db, order_id)


@router.get("/{order_item_id}", response_model=OrderItemRead)
def get_order_item(order_item_id: int, db: Session = Depends(get_db)):
    return crud_order_items.get_order_item(order_item_id, db)


@router.post("/", response_model=OrderItemRead, status_code=status.HTTP_201_CREATED)
def create_order_item(
    item: OrderItemStandaloneCreate, db: Session = Depends(get_db)
):
    return crud_order_items.create_order_item(db, item)


@router.put("/{order_item_id}", response_model=OrderItemRead)
def update_order_item(
    order_item_id: int, item: OrderItemUpdate, db: Session = Depends(get_db)
):
    return crud_order_items.update_order_item(db, order_item_id, item)


@router.delete("/{order_item_id}", status_code=status.HTTP_200_OK)
def delete_order_item(order_item_id: int, db: Session = Depends(get_db)):
    return crud_order_items.delete_order_item(order_item_id, db)
