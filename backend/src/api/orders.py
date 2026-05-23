from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.src.db import get_db
from backend.src.schema import OrderCreate, OrderRead, OrderUpdate
from backend.src.crud import orders as crud_orders

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.get("/", response_model=list[OrderRead])
def list_orders(db: Session = Depends(get_db)):
    return crud_orders.get_orders(db)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return crud_orders.get_order(order_id, db)


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    return crud_orders.create_order(db, order)


@router.put("/{order_id}", response_model=OrderRead)
def update_order(order_id: int, order: OrderUpdate, db: Session = Depends(get_db)):
    return crud_orders.update_order(db, order_id, order)


@router.delete("/{order_id}", status_code=status.HTTP_200_OK)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    return crud_orders.delete_order(order_id, db)
