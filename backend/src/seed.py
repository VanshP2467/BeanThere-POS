from typing import List

from sqlalchemy.orm import Session

from backend.src.db import Base, engine, SessionLocal
from backend.src.models import Category, MenuItem, Modifier


def seed():
    # Drop all tables
    Base.metadata.drop_all(bind=engine)

    # Recreate all tables
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    if db.query(Category).first():
        print("Seed data already present.")
        return

    # create tables
    Base.metadata.create_all(bind=engine)

    coffee: Category = Category(name="Coffee")
    matcha: Category = Category(name="Matcha")
    lemonade: Category = Category(name="Lemonade")

    # Create modifiers
    extra_shot = Modifier(name="Extra Shot", price_change=0.50)
    vanilla_syrup = Modifier(name="Vanilla Syrup", price_change=0.25)
    oat_milk = Modifier(name="Oat Milk", price_change=0.5)
    dairy_milk = Modifier(name="Milk", price_change=0.0)

    db.add_all([coffee, matcha, lemonade, extra_shot, vanilla_syrup])
    db.commit()

    coffee_items: List[MenuItem] = [
        MenuItem(
            name="Espresso",
            description="Classic italian espresso.",
            price=3.00,
            tags=["hot", "coffee"],
            category_id=coffee.id,
            modifiers=[extra_shot],
        ),
        MenuItem(
            name="Americano",
            description="Espresso with added hot water for a smoother flavor.",
            price=3.50,
            tags=["hot", "coffee"],
            modifiers=[extra_shot, oat_milk, dairy_milk],
            category_id=coffee.id,
        ),
        MenuItem(
            name="Iced Americano",
            description="Espresso poured over ice and cold water.",
            price=3.75,
            tags=["iced", "coffee"],
            category_id=coffee.id,
        ),
        MenuItem(
            name="Cappuccino",
            description="Espresso topped with steamed milk and a thick layer of foam.",
            price=4.25,
            modifiers=[extra_shot, oat_milk, dairy_milk, vanilla_syrup],
            tags=["hot", "milk"],
            category_id=coffee.id,
        ),
        MenuItem(
            name="Latte",
            description="Smooth espresso blended with steamed milk and light foam.",
            price=4.50,
            modifiers=[extra_shot, oat_milk, dairy_milk, vanilla_syrup],
            tags=["hot", "milk"],
            category_id=coffee.id,
        ),
        MenuItem(
            name="Iced Latte",
            description="Espresso mixed with cold milk and ice.",
            price=4.75,
            modifiers=[extra_shot, oat_milk, dairy_milk, vanilla_syrup],
            tags=["iced", "milk"],
            category_id=coffee.id,
        ),
        MenuItem(
            name="Flat White",
            description="Silky microfoam over a rich shot of espresso.",
            modifiers=[extra_shot, oat_milk, dairy_milk, vanilla_syrup],
            price=4.50,
            tags=["hot", "milk"],
            category_id=coffee.id,
        ),
        MenuItem(
            name="Cortado",
            description="Equal parts espresso and steamed milk for a balanced taste.",
            modifiers=[extra_shot, oat_milk, dairy_milk, vanilla_syrup],
            price=4.00,
            tags=["hot", "milk"],
            category_id=coffee.id,
        ),
        MenuItem(
            name="Mocha",
            description="Espresso with chocolate syrup and steamed milk, topped with whipped cream.",
            modifiers=[extra_shot, oat_milk, dairy_milk, vanilla_syrup],
            price=5.00,
            tags=["hot", "chocolate", "coffee"],
            category_id=coffee.id,
        ),
        MenuItem(
            name="Iced Mocha",
            description="Chilled espresso with chocolate syrup, milk, and ice.",
            modifiers=[extra_shot, oat_milk, dairy_milk, vanilla_syrup],
            price=5.25,
            tags=["iced", "chocolate", "coffee"],
            category_id=coffee.id,
        ),
    ]

    matcha_items: List[MenuItem] = [
        MenuItem(
            name="Matcha Latte",
            description="Classic Japanese matcha tea with steamed milk.",
            modifiers=[extra_shot, oat_milk, dairy_milk, vanilla_syrup],
            price=4.50,
            category_id=matcha.id,
            tags=["hot", "milk", "matcha"],
        ),
        MenuItem(
            name="Iced Matcha Latte",
            description="Classic Japanese matcha tea with chilled milk and ice.",
            modifiers=[extra_shot, oat_milk, dairy_milk, vanilla_syrup],
            price=4.50,
            category_id=matcha.id,
            tags=["Iced", "milk", "matcha"],
        ),
        MenuItem(
            name="Matcha Green Tea",
            description="Classic Japanese matcha tea hot water.",
            modifiers=[extra_shot, vanilla_syrup],
            price=4.50,
            category_id=matcha.id,
            tags=["hot", "matcha"],
        ),
    ]

    lemonade_items: List[MenuItem] = [
        MenuItem(
            name="Classic Lemonade",
            description="Citrusy still lemonade made with fresh lime juice.",
            price=3.50,
            category_id=lemonade.id,
            tags=["iced", "lemonade"],
        ),
        MenuItem(
            name="Sparkling Lemonade",
            description="Refreshing sparkling lemonade.",
            price=3.75,
            category_id=lemonade.id,
            tags=["iced", "lemonade"],
        ),
    ]
    db.add_all(coffee_items + matcha_items + lemonade_items)
    db.commit()


if __name__ == "__main__":
    seed()
