import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.src.models import Category
from backend.src.schema import CategoryCreate, CategoryUpdate

logger = logging.getLogger(__name__)


def get_categories(db: Session):
    try:
        return db.query(Category).all()
    except SQLAlchemyError as exc:
        logger.exception("Failed to fetch categories", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories.",
        )


def get_category(category_id: int, db: Session):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )
    return category


def create_category(category: CategoryCreate, db: Session):
    db_category = Category(name=category.name)
    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category '{category.name}' already exists",
        )
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to create category", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create category.",
        )


def update_category(category_id: int, category: CategoryUpdate, db: Session):
    db_category = get_category(category_id, db)
    update_data = category.model_dump(exclude_unset=True)
    if not update_data:
        return db_category

    for key, value in update_data.items():
        setattr(db_category, key, value)
    try:
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category name '{category.name}' already exists",
        )
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to update category %s", category_id, exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update category.",
        )


def delete_category(category_id: int, db: Session):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )

    try:
        db.delete(category)
        db.commit()
        return {"message": f"Category '{category.name}' deleted successfully"}
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to delete category %s", category_id, exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete category.",
        )
