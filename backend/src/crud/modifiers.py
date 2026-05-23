from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src.models import Modifier
from backend.src.schema import ModifierCreate, ModifierUpdate


def get_modifiers(db: Session):
    try:
        return db.query(Modifier).all()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {exc.__class__.__name__}: {exc}",
        )


def get_modifier(modifier_id: int, db: Session):
    modifier = db.query(Modifier).filter(Modifier.id == modifier_id).first()
    if not modifier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modifier with id {modifier_id} not found",
        )
    return modifier


def create_modifier(modifier: ModifierCreate, db: Session):
    db_modifier = Modifier(name=modifier.name, price_change=modifier.price_change)
    try:
        db.add(db_modifier)
        db.commit()
        db.refresh(db_modifier)
        return db_modifier
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Modifier '{modifier.name}' already exists",
        )
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create modifier: {exc.__class__.__name__}: {exc}",
        )


def update_modifier(modifier_id: int, modifier: ModifierUpdate, db: Session):
    db_modifier = get_modifier(modifier_id, db)
    update_data = modifier.model_dump(exclude_unset=True)
    if not update_data:
        return db_modifier

    for key, value in update_data.items():
        setattr(db_modifier, key, value)

    try:
        db.commit()
        db.refresh(db_modifier)
        return db_modifier
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Modifier '{modifier_id}' update conflicts with existing data",
        )
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update modifier: {exc.__class__.__name__}: {exc}",
        )


def delete_modifier(modifier_id: int, db: Session):
    db_modifier = get_modifier(modifier_id, db)
    try:
        db.delete(db_modifier)
        db.commit()
        return {"message": f"Modifier '{db_modifier.name}' deleted successfully"}
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete modifier: {exc.__class__.__name__}: {exc}",
        )
