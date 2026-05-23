from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src import models, schema


def _get_category(db: Session, category_id: int) -> models.Category:
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found",
        )
    return category


def _get_modifiers(db: Session, modifier_ids: list[int]) -> list[models.Modifier]:
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {exc.__class__.__name__}: {exc}",
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
    _get_category(db, item.category_id)
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {exc.__class__.__name__}: {exc}",
        )


def update_menu_item(db: Session, item_id: int, updated_item: schema.MenuItemUpdate):
    db_item = get_menu_item(db, item_id)
    update_data = updated_item.model_dump(exclude_unset=True)

    if "category_id" in update_data and update_data["category_id"] is not None:
        _get_category(db, update_data["category_id"])

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update menu item: {exc.__class__.__name__}: {exc}",
        )


def delete_menu_item(db: Session, item_id: int):
    db_item = get_menu_item(db, item_id)
    try:
        db.delete(db_item)
        db.commit()
        return {"message": f"Menu item {item_id} deleted successfully."}
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete menu item: {exc.__class__.__name__}: {exc}",
        )
