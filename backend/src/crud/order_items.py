from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src import models, schema


def _get_order(db: Session, order_id: int) -> models.Order:
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found",
        )
    return order


def _get_menu_item(db: Session, item_id: int) -> models.MenuItem:
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with id {item_id} not found",
        )
    return menu_item


def get_order_items(db: Session, order_id: int | None = None):
    try:
        query = db.query(models.OrderItem)
        if order_id is not None:
            query = query.filter(models.OrderItem.order_id == order_id)
        return query.all()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {exc.__class__.__name__}: {exc}",
        )


def get_order_item(order_item_id: int, db: Session):
    order_item = (
        db.query(models.OrderItem)
        .filter(models.OrderItem.id == order_item_id)
        .first()
    )
    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order item with id {order_item_id} not found",
        )
    return order_item


def create_order_item(db: Session, item: schema.OrderItemStandaloneCreate):
    _get_order(db, item.order_id)
    _get_menu_item(db, item.item_id)
    db_item = models.OrderItem(
        order_id=item.order_id,
        item_id=item.item_id,
        quantity=item.quantity,
        modifiers=item.modifiers,
    )
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order item: {exc.__class__.__name__}: {exc}",
        )


def update_order_item(
    db: Session, order_item_id: int, item: schema.OrderItemUpdate
):
    db_item = get_order_item(order_item_id, db)
    update_data = item.model_dump(exclude_unset=True)
    if not update_data:
        return db_item

    if "item_id" in update_data and update_data["item_id"] is not None:
        _get_menu_item(db, update_data["item_id"])

    for key, value in update_data.items():
        setattr(db_item, key, value)

    try:
        db.commit()
        db.refresh(db_item)
        return db_item
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update order item: {exc.__class__.__name__}: {exc}",
        )


def delete_order_item(order_item_id: int, db: Session):
    db_item = get_order_item(order_item_id, db)
    try:
        db.delete(db_item)
        db.commit()
        return {"message": f"Order item {order_item_id} deleted successfully."}
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete order item: {exc.__class__.__name__}: {exc}",
        )
