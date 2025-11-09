from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from backend.src.db import get_db
from backend.src.schema import CategorySchema
from backend.src.crud import categories as crud_categories

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get("/", response_model=List[CategorySchema])
def list_categories(db: Session = Depends(get_db)):
    return crud_categories.get_categories(db)


@router.get("/{category_id}", response_model=CategorySchema)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return crud_categories.get_category(category_id, db)


@router.post(
    "/",
    response_model=CategorySchema,
    status_code=status.HTTP_201_CREATED
)
def create_category(category: CategorySchema, db: Session = Depends(get_db)):
    return crud_categories.create_category(category, db)


@router.put("/{category_id}", response_model=CategorySchema)
def update_category(category_id: int, category: CategorySchema, db: Session = Depends(get_db)):
    return crud_categories.update_category(category_id, category, db)


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    return crud_categories.delete_category(category_id, db)
