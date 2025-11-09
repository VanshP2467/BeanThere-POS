from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.src.db import get_db
from backend.src import crud, schema

router = APIRouter(prefix="/menu_items", tags=["menu_items"])


@router.get("/", response_model=list[schema.MenuItemSchema])
def list_menu_items(db: Session = Depends(get_db)):
    return crud.menu_items.get_menu_items(db)


@router.post("/", response_model=schema.MenuItemSchema)
def create_menu_item(item: schema.MenuItemCreate, db: Session = Depends(get_db)):
    return crud.menu_items.create_menu_item(db, item)
