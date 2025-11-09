from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status

from backend.src import models, schema


def get_menu_items(db: Session):
    try:
        return db.query(models.MenuItem).all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def get_menu_item(db: Session, item_id: int):
    item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with id {item_id} not found",
        )
    return item


def create_menu_item(db: Session, item: schema.MenuItemCreate):
    db_item = models.MenuItem(**item.model_dump())
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A menu item named '{item.name}' already exists.",
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def update_menu_item(db: Session, item_id: int, updated_item: schema.MenuItemUpdate):
    db_item = get_menu_item(db, item_id)
    for key, value in updated_item.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    try:
        db.commit()
        db.refresh(db_item)
        return db_item
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update menu item: {str(e)}",
        )


def delete_menu_item(db: Session, item_id: int):
    db_item = get_menu_item(db, item_id)
    try:
        db.delete(db_item)
        db.commit()
        return {"message": f"Menu item {item_id} deleted successfully."}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete menu item: {str(e)}",
        )
