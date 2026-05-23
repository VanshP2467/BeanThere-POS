from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from backend.src.db import get_db
from backend.src.schema import ModifierCreate, ModifierRead, ModifierUpdate
from backend.src.crud import modifiers as crud_modifiers

router = APIRouter(
    prefix="/modifiers",
    tags=["Modifiers"],
)


@router.get("/", response_model=List[ModifierRead])
def list_modifiers(db: Session = Depends(get_db)):
    return crud_modifiers.get_modifiers(db)


@router.get("/{modifier_id}", response_model=ModifierRead)
def get_modifier(modifier_id: int, db: Session = Depends(get_db)):
    return crud_modifiers.get_modifier(modifier_id, db)


@router.post("/", response_model=ModifierRead, status_code=status.HTTP_201_CREATED)
def create_modifier(modifier: ModifierCreate, db: Session = Depends(get_db)):
    return crud_modifiers.create_modifier(modifier, db)


@router.put("/{modifier_id}", response_model=ModifierRead)
def update_modifier(
    modifier_id: int, modifier: ModifierUpdate, db: Session = Depends(get_db)
):
    return crud_modifiers.update_modifier(modifier_id, modifier, db)


@router.delete("/{modifier_id}", status_code=status.HTTP_200_OK)
def delete_modifier(modifier_id: int, db: Session = Depends(get_db)):
    return crud_modifiers.delete_modifier(modifier_id, db)
