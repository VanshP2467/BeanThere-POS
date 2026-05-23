from fastapi import FastAPI, HTTPException, Depends
from sqladmin import ModelView, Admin

from backend.src.api import menu_items, categories
from backend.src.db import engine, SessionLocal
from backend.src.models import MenuItem

from sqlalchemy.orm import Session
from typing import List
from backend.src.models import Category, Order, Modifier
from backend.src.schema import *
# # Create tables (only for dev)
# Base.metadata.create_all(bind=engine)
#
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="BeanThere POS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
    ],  # SvelteKit dev & preview
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#
#
# Dependency: get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", tags=["Root"])
def root():
    return {"status": "API is running"}


#

admin = Admin(app, engine)


# create model views
class MenuItemAdmin(ModelView, model=MenuItem):
    column_list = [MenuItem.id, MenuItem.name, MenuItem.price, MenuItem.active]
    name = "Menu Item"
    name_plural = "Menu Items"


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.name]


class ModifierAdmin(ModelView, model=Modifier):
    column_list = [Modifier.id, Modifier.name, Modifier.price_change]


# add them to admin
admin.add_view(MenuItemAdmin)
admin.add_view(CategoryAdmin)
admin.add_view(ModifierAdmin)


# Categories endpoints
@app.get("/categories", response_model=List[CategoryBase], tags=["Categories"])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@app.get(
    "/categories/{category_id}", response_model=CategoryBase, tags=["Categories"]
)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.post("/categories", response_model=CategoryBase)
def create_category(category: CategoryBase, db: Session = Depends(get_db)):
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@app.put("/categories/{category_id}", response_model=CategoryBase)
def update_category(
    category_id: int, category: CategoryBase, db: Session = Depends(get_db)
):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db_category.name = category.name
    db.commit()
    db.refresh(db_category)
    return db_category


@app.delete("/categories/{category_id}", response_model=CategoryBase)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"message": "Category deleted"}


# MenuItems endpoints
@app.get("/menu_items", response_model=List[MenuItemBase], tags=["MenuItems"])
def get_menu_items(db: Session = Depends(get_db)):
    return db.query(MenuItem).all()


@app.get("/menu_items/{item_id}", response_model=MenuItemBase, tags=["MenuItems"])
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="MenuItem not found")
    return item


@app.post("/menu_items", response_model=MenuItemBase, tags=["MenuItems"])
def create_menu_item(item: MenuItemBase, db: Session = Depends(get_db)):
    db_item = MenuItem(
        name=item.name,
        description=item.description,
        price=item.price,
        tags=item.tags,
        category_id=item.category.id if item.category else None,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.put("/menu_items/{item_id}", response_model=MenuItemBase, tags=["MenuItems"])
def update_menu_item(item_id: int, item: MenuItemBase, db: Session = Depends(get_db)):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="MenuItem not found")
    db_item.name = item.name
    db_item.description = item.description
    db_item.price = item.price
    db_item.tags = item.tags
    if item.category:
        db_item.category_id = item.category.id
    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/menu_items/{item_id}", response_model=MenuItemBase, tags=["MenuItems"])
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="MenuItem not found")
    db.delete(db_item)
    db.commit()
    return {"message": "MenuItem deleted"}


# Orders endpoints
@app.get("/orders", response_model=List[OrderBase])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@app.get("/orders/{order_id}", response_model=OrderBase)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.post("/orders", response_model=OrderBase)
def create_order(order: OrderBase, db: Session = Depends(get_db)):
    db_order = Order(status=order.status)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(db_order)
    db.commit()
    return {"detail": "Order deleted"}


app.include_router(menu_items.router)
app.include_router(categories.router)
# app.include_router(order.router)
