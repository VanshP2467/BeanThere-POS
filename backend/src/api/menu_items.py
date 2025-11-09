from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from backend.src.db import get_db
from backend.src import crud, schema

router = APIRouter(
    prefix="/menu_items",
    tags=["Menu Items"],
)


@router.get("/", response_model=List[schema.MenuItemSchema])
def list_menu_items(db: Session = Depends(get_db)):
    """Retrieve all menu items"""
    return crud.menu_items.get_menu_items(db)


@router.get("/{item_id}", response_model=schema.MenuItemSchema)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    """Retrieve a single menu item by ID"""
    return crud.menu_items.get_menu_item(db, item_id)


@router.post(
    "/",
    response_model=schema.MenuItemSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_menu_item(item: schema.MenuItemCreate, db: Session = Depends(get_db)):
    """Create a new menu item"""
    return crud.menu_items.create_menu_item(db, item)


@router.put("/{item_id}", response_model=schema.MenuItemSchema)
def update_menu_item(
    item_id: int, item: schema.MenuItemUpdate, db: Session = Depends(get_db)
):
    """Update a menu item"""
    return crud.menu_items.update_menu_item(db, item_id, item)


@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a menu item"""
    return crud.menu_items.delete_menu_item(db, item_id)
