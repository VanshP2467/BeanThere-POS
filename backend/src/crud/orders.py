from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src import models, schema
from backend.src.crud.helpers import get_menu_item_or_404, get_order_or_404


def get_orders(db: Session):
    try:
        return db.query(models.Order).all()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {exc.__class__.__name__}: {exc}",
        )


def get_order(order_id: int, db: Session):
    return get_order_or_404(db, order_id)


def create_order(db: Session, order: schema.OrderCreate):
    db_order = models.Order(status=order.status)
    try:
        db.add(db_order)
        db.flush()
        for item in order.items:
            get_menu_item_or_404(db, item.item_id)
            db_item = models.OrderItem(
                order=db_order,
                item_id=item.item_id,
                quantity=item.quantity,
                modifiers=item.modifiers,
            )
            db.add(db_item)
        db.commit()
        db.refresh(db_order)
        return db_order
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {exc.__class__.__name__}: {exc}",
        )


def update_order(db: Session, order_id: int, order: schema.OrderUpdate):
    db_order = get_order_or_404(db, order_id)
    update_data = order.model_dump(exclude_unset=True)
    if not update_data:
        return db_order

    for key, value in update_data.items():
        setattr(db_order, key, value)

    try:
        db.commit()
        db.refresh(db_order)
        return db_order
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update order: {exc.__class__.__name__}: {exc}",
        )


def delete_order(order_id: int, db: Session):
    db_order = get_order(order_id, db)
    try:
        db.delete(db_order)
        db.commit()
        return {"message": f"Order {order_id} deleted successfully."}
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete order: {exc.__class__.__name__}: {exc}",
        )
