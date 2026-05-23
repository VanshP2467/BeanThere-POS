import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src import models, schema
from backend.src.crud.categories import get_category

logger = logging.getLogger(__name__)


def _get_modifiers(
    db: Session, modifier_ids: list[int] | None
) -> list[models.Modifier]:
    if not modifier_ids:
        return []
    modifiers = (
        db.query(models.Modifier)
        .filter(models.Modifier.id.in_(modifier_ids))
        .all()
    )
    found_ids = {modifier.id for modifier in modifiers}
    missing = sorted(set(modifier_ids) - found_ids)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modifiers not found: {missing}",
        )
    return modifiers


def get_menu_items(db: Session):
    try:
        return db.query(models.MenuItem).all()
    except SQLAlchemyError as exc:
        logger.exception("Failed to fetch menu items", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch menu items.",
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
    get_category(item.category_id, db)
    db_item = models.MenuItem(
        name=item.name,
        description=item.description,
        price=item.price,
        tags=item.tags,
        active=item.active,
        category_id=item.category_id,
    )
    db_item.modifiers = _get_modifiers(db, item.modifier_ids)
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
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to create menu item", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create menu item.",
        )


def update_menu_item(db: Session, item_id: int, updated_item: schema.MenuItemUpdate):
    db_item = get_menu_item(db, item_id)
    update_data = updated_item.model_dump(exclude_unset=True)

    if "category_id" in update_data and update_data["category_id"] is not None:
        get_category(update_data["category_id"], db)

    modifier_ids = update_data.pop("modifier_ids", None)

    for key, value in update_data.items():
        setattr(db_item, key, value)

    if modifier_ids is not None:
        db_item.modifiers = _get_modifiers(db, modifier_ids)

    try:
        db.commit()
        db.refresh(db_item)
        return db_item
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate or invalid data while updating menu item {item_id}.",
        )
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to update menu item %s", item_id, exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update menu item.",
        )


def delete_menu_item(db: Session, item_id: int):
    db_item = get_menu_item(db, item_id)
    try:
        db.delete(db_item)
        db.commit()
        return {"message": f"Menu item {item_id} deleted successfully."}
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to delete menu item %s", item_id, exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete menu item.",
        )
